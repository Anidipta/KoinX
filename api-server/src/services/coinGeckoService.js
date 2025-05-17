const axios = require('axios');
const config = require('../config');

/**
 * Service to interact with CoinGecko API
 */
class CoinGeckoService {
  constructor() {
    this.apiUrl = config.coinGeckoApiUrl;
  }

  /**
   * Fetch current cryptocurrency prices and market data
   * @returns {Promise<Object>} - Cryptocurrency data
   */
  async fetchCryptoData() {
    try {
      const coins = config.supportedCoins.join(',');
      const response = await axios.get(`${this.apiUrl}/coins/markets`, {
        params: {
          vs_currency: 'usd',
          ids: coins,
          order: 'market_cap_desc',
          per_page: 100,
          page: 1,
          sparkline: false,
          price_change_percentage: '24h'
        }
      });

      return response.data;
    } catch (error) {
      console.error('Error fetching data from CoinGecko:', error.message);
      throw new Error(`Failed to fetch data from CoinGecko: ${error.message}`);
    }
  }
}

module.exports = new CoinGeckoService();