const { connect, JSONCodec } = require('nats');
const config = require('../config');
const dbService = require('./dbService');

class NatsService {
  constructor() {
    this.connection = null;
    this.jsonCodec = JSONCodec();
  }

  /**
   * Connect to NATS server
   */
  async connect() {
    try {
      this.connection = await connect({ servers: config.natsUrl });
      console.log(`Connected to NATS at ${config.natsUrl}`);
      this.setupSubscriptions();
    } catch (error) {
      console.error('Failed to connect to NATS:', error);
      // Retry connection after delay
      setTimeout(() => this.connect(), 5000);
    }
  }

  /**
   * Setup subscriptions to NATS topics
   */
  setupSubscriptions() {
    const subscription = this.connection.subscribe('crypto.update');
    console.log('Subscribed to crypto.update topic');
    
    // Process messages
    (async () => {
      for await (const message of subscription) {
        try {
          const data = this.jsonCodec.decode(message.data);
          console.log('Received message:', data);
          
          if (data.trigger === 'update') {
            console.log('Triggering crypto stats update...');
            await dbService.storeCryptoStats();
          }
        } catch (error) {
          console.error('Error processing message:', error);
        }
      }
    })();
  }

  /**
   * Close NATS connection
   */
  async close() {
    if (this.connection) {
      await this.connection.drain();
      console.log('NATS connection closed');
    }
  }
}

module.exports = new NatsService();