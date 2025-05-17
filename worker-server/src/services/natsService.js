const { connect, JSONCodec } = require('nats');
const config = require('../config');

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
      return this.connection;
    } catch (error) {
      console.error('Failed to connect to NATS:', error);
      throw error;
    }
  }

  /**
   * Publish a message to a NATS subject
   * @param {string} subject - NATS subject/topic
   * @param {Object} data - Message data
   */
  async publish(subject, data) {
    try {
      if (!this.connection) {
        await this.connect();
      }
      
      this.connection.publish(subject, this.jsonCodec.encode(data));
      console.log(`Published message to ${subject}:`, data);
    } catch (error) {
      console.error(`Error publishing message to ${subject}:`, error);
      throw error;
    }
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