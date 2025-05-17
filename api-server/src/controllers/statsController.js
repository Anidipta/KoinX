const dbService = require('../services/dbService');
const config = require('../config');

/**
 * Controller for cryptocurrency statistics endpoints
 */
class StatsController {
  /**
   * Get latest statistics for a specific cryptocurrency
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  async getStats(req, res) {
    try {
      const { coin } = req.query;
      
      if (!coin) {
        return res.status(400).json({ error: 'Coin parameter is required' });
      }
      
      if (!config.supportedCoins.includes(coin)) {
        return res.status(400).json({ 
          error: `Unsupported coin. Must be one of: ${config.supportedCoins.join(', ')}` 
        });
      }
      
      const stats = await dbService.getLatestStats(coin);
      res.json(stats);
    } catch (error) {
      console.error('Error in getStats:', error);
      res.status(500).json({ error: error.message || 'Internal server error' });
    }
  }
  
  /**
   * Get price deviation for a specific cryptocurrency
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  async getDeviation(req, res) {
    try {
      const { coin } = req.query;
      
      if (!coin) {
        return res.status(400).json({ error: 'Coin parameter is required' });
      }
      
      if (!config.supportedCoins.includes(coin)) {
        return res.status(400).json({ 
          error: `Unsupported coin. Must be one of: ${config.supportedCoins.join(', ')}` 
        });
      }
      
      const deviation = await dbService.calculatePriceDeviation(coin);
      res.json({ deviation });
    } catch (error) {
      console.error('Error in getDeviation:', error);
      res.status(500).json({ error: error.message || 'Internal server error' });
    }
  }
  
  /**
   * Manually trigger cryptocurrency data update
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  async triggerUpdate(req, res) {
    try {
      await dbService.storeCryptoStats();
      res.json({ message: 'Cryptocurrency stats updated successfully' });
    } catch (error) {
      console.error('Error in triggerUpdate:', error);
      res.status(500).json({ error: error.message || 'Internal server error' });
    }
  }
}

module.exports = new StatsController();