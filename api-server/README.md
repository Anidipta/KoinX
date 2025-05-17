# API Server for Cryptocurrency Statistics

This server provides cryptocurrency statistics by fetching data from the CoinGecko API and storing it in MongoDB.

## Features

- Fetches and stores cryptocurrency data (Bitcoin, Ethereum, and Matic Network)
- Provides API endpoints for retrieving statistics and calculating price deviation
- Subscribes to events from the worker server to periodically update cryptocurrency data

## Prerequisites

- Node.js (v16 or higher)
- MongoDB
- NATS server

## Setup

1. Clone the repository
2. Navigate to the api-server directory:
   ```
   cd api-server
   ```
3. Install dependencies:
   ```
   npm install
   ```
4. Create a `.env` file based on `.env.example` and fill in your configuration
5. Start the server:
   ```
   npm start
   ```
   For development with auto-reload:
   ```
   npm run dev
   ```

## Environment Variables

Create a `.env` file with the following variables:

```
PORT=3000
MONGODB_URI=mongodb://localhost:27017/crypto-stats
NATS_URL=nats://localhost:4222
COINGECKO_API_URL=https://api.coingecko.com/api/v3
```

## API Endpoints

### Get Cryptocurrency Statistics

```
GET /stats?coin=bitcoin
```

Query Parameters:
- `coin`: One of `bitcoin`, `ethereum`, or `matic-network`

Response:
```json
{
  "price": 40000,
  "marketCap": 800000000,
  "24hChange": 3.4
}
```

### Get Price Deviation

```
GET /deviation?coin=bitcoin
```

Query Parameters:
- `coin`: One of `bitcoin`, `ethereum`, or `matic-network`

Response:
```json
{
  "deviation": 4082.48
}
```

## Architecture

The server consists of the following components:

- MongoDB models for storing cryptocurrency data
- Services for interacting with CoinGecko API and NATS
- Controllers for handling API requests
- Subscription to NATS events for triggering data updates

## Running with Docker

```bash
docker build -t api-server .
docker run -p 3000:3000 --env-file .env api-server
```