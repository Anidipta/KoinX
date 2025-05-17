const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const config = require('./config');
const statsController = require('./controllers/statsController');
const natsService = require('./services/natsService');
const dbService = require('./services/dbService');

// Create Express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/stats', statsController.getStats);
app.get('/deviation', statsController.getDeviation);
app.post('/trigger-update', statsController.triggerUpdate);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date() });
});

// Connect to MongoDB
mongoose.connect(config.mongodbUri)
  .then(() => {
    console.log(`Connected to MongoDB at ${config.mongodbUri}`);
    
    // Connect to NATS
    natsService.connect()
      .catch(err => console.error('Failed to connect to NATS:', err));
    
    // Initial data fetch
    dbService.storeCryptoStats()
      .then(() => console.log('Initial cryptocurrency data stored successfully'))
      .catch(err => console.error('Error storing initial cryptocurrency data:', err));
  })
  .catch(err => {
    console.error('Failed to connect to MongoDB:', err);
    process.exit(1);
  });

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('Shutting down server...');
  await natsService.close();
  await mongoose.connection.close();
  process.exit(0);
});

module.exports = app;