require('dotenv').config();

module.exports = {
  port: process.env.PORT || 3000,
  mongodbUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/crypto-stats',
  natsUrl: process.env.NATS_URL || 'nats://localhost:4222',
  coinGeckoApiUrl: process.env.COINGECKO_API_URL || 'https://api.coingecko.com/api/v3',
  supportedCoins: ['bitcoin', 'ethereum', 'matic-network']
};