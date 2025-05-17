const Crypto = require('../models/Crypto');
const coinGeckoService = require('./coinGeckoService');
const config = require('../config');

class DbService {
  /**
   * Store cryptocurrency statistics in the database
   */
  async storeCryptoStats() {
    try {
      console.log('Fetching cryptocurrency data from CoinGecko...');
      const cryptoData = await coinGeckoService.fetchCryptoData();
      
      const savePromises = cryptoData.map(coin => {
        const cryptoRecord = new Crypto({
          coin: coin.id,
          price: coin.current_price,
          marketCap: coin.market_cap,
          change24h: coin.price_change_percentage_24h || 0
        });
        
        return cryptoRecord.save();
      });
      
      await Promise.all(savePromises);
      console.log(`Successfully stored data for ${cryptoData.length} coins`);
      return true;
    } catch (error) {
      console.error('Error storing cryptocurrency data:', error);
      throw error;
    }
  }

  /**
   * Get the latest statistics for a specific cryptocurrency
   * @param {string} coin - Cryptocurrency identifier
   * @returns {Promise<Object>} - Latest cryptocurrency statistics
   */
  async getLatestStats(coin) {
    try {
      if (!config.supportedCoins.includes(coin)) {
        throw new Error(`Unsupported coin: ${coin}`);
      }
      
      const latestRecord = await Crypto.findOne({ coin })
        .sort({ timestamp: -1 })
        .exec();
      
      if (!latestRecord) {
        throw new Error(`No data found for ${coin}`);
      }
      
      return {
        price: latestRecord.price,
        marketCap: latestRecord.marketCap,
        "24hChange": latestRecord.change24h
      };
    } catch (error) {
      console.error(`Error fetching latest stats for ${coin}:`, error);
      throw error;
    }
  }

  /**
   * Calculate the standard deviation of price for a specific cryptocurrency
   * @param {string} coin - Cryptocurrency identifier
   * @returns {Promise<number>} - Standard deviation of price
   */
  async calculatePriceDeviation(coin) {
    try {
      if (!config.supportedCoins.includes(coin)) {
        throw new Error(`Unsupported coin: ${coin}`);
      }
      
      const records = await Crypto.find({ coin })
        .sort({ timestamp: -1 })
        .limit(100)
        .select('price')
        .exec();
      
      if (records.length === 0) {
        throw new Error(`No data found for ${coin}`);
      }
      
      const prices = records.map(record => record.price);
      
      // Calculate standard deviation
      const mean = prices.reduce((sum, price) => sum + price, 0) / prices.length;
      const squaredDifferences = prices.map(price => Math.pow(price - mean, 2));
      const variance = squaredDifferences.reduce((sum, diff) => sum + diff, 0) / prices.length;
      const stdDeviation = Math.sqrt(variance);
      
      return Number(stdDeviation.toFixed(2));
    } catch (error) {
      console.error(`Error calculating price deviation for ${coin}:`, error);
      throw error;
    }
  }
}

module.exports = new DbService();