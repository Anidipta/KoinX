const cron = require('node-cron');
const natsService = require('../services/natsService');
const config = require('../config');

class Scheduler {
  constructor() {
    this.jobs = [];
  }

  /**
   * Initialize the scheduler and set up jobs
   */
  initialize() {
    this.setupCryptoUpdateJob();
    console.log('Scheduler initialized with jobs');
  }

  /**
   * Set up the job to trigger cryptocurrency data updates
   */
  setupCryptoUpdateJob() {
    console.log(`Setting up crypto update job with schedule: ${config.cronSchedule}`);
    
    if (!cron.validate(config.cronSchedule)) {
      console.error(`Invalid cron schedule: ${config.cronSchedule}`);
      return;
    }
    
    const job = cron.schedule(config.cronSchedule, async () => {
      try {
        console.log(`Running scheduled job at ${new Date().toISOString()}`);
        
        // Publish update event to NATS
        await natsService.publish('crypto.update', { 
          trigger: 'update',
          timestamp: new Date().toISOString()
        });
        
        console.log('Crypto update event published successfully');
      } catch (error) {
        console.error('Error executing crypto update job:', error);
      }
    });
    
    this.jobs.push(job);
    console.log('Crypto update job scheduled successfully');
  }

  /**
   * Stop all scheduled jobs
   */
  stopAll() {
    this.jobs.forEach(job => job.stop());
    console.log('All scheduled jobs stopped');
  }
}

module.exports = new Scheduler();