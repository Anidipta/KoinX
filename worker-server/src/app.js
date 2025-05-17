const http = require('http');
const natsService = require('./services/natsService');
const scheduler = require('./utils/scheduler');
const config = require('./config');

// Create a simple HTTP server for health checks
const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'OK', 
      timestamp: new Date().toISOString() 
    }));
  } else {
    res.writeHead(404);
    res.end();
  }
});

// Initialize services
async function initialize() {
  try {
    // Connect to NATS
    await natsService.connect();
    
    // Initialize scheduler
    scheduler.initialize();
    
    // Send initial update event
    await natsService.publish('crypto.update', { 
      trigger: 'update',
      timestamp: new Date().toISOString() 
    });
    
    console.log('Worker server initialized successfully');
  } catch (error) {
    console.error('Error initializing worker server:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('Shutting down worker server...');
  scheduler.stopAll();
  await natsService.close();
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });
});

module.exports = {
  server,
  initialize
};