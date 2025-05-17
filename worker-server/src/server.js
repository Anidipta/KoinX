const { server, initialize } = require('./app');
const config = require('./config');

const PORT = config.port;

// Start the server
server.listen(PORT, async () => {
  console.log(`Worker server running on port ${PORT}`);
  
  // Initialize services
  await initialize();
});