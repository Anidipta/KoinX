const mongoose = require('mongoose');

const cryptoSchema = new mongoose.Schema({
  coin: {
    type: String,
    required: true,
    enum: ['bitcoin', 'ethereum', 'matic-network']
  },
  price: {
    type: Number,
    required: true
  },
  marketCap: {
    type: Number,
    required: true
  },
  change24h: {
    type: Number,
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

// Create an index for faster querying by coin and timestamp
cryptoSchema.index({ coin: 1, timestamp: -1 });

const Crypto = mongoose.model('Crypto', cryptoSchema);

module.exports = Crypto;