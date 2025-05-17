# KoinX - Cryptocurrency Statistics System

This project consists of two Node.js servers that work together to collect, store, and expose cryptocurrency statistics.

## System Architecture

![System Architecture](https://i.imgur.com/XXXXXX.png)

### Components

1. **API Server (`api-server`)**
   - Provides REST APIs for retrieving cryptocurrency statistics
   - Stores cryptocurrency data in MongoDB
   - Subscribes to events from the worker server via NATS

2. **Worker Server (`worker-server`)**
   - Runs a scheduled job every 15 minutes
   - Publishes events to NATS to trigger data updates

3. **MongoDB**
   - Stores cryptocurrency statistics
   - Maintains historical data for deviation calculations

4. **NATS**
   - Provides message queue functionality for inter-server communication

## Data Flow

1. The worker server runs a scheduled job every 15 minutes
2. When triggered, the worker server publishes an event to the NATS topic `crypto.update`
3. The API server, subscribed to the `crypto.update` topic, receives the event
4. Upon receiving the event, the API server fetches current cryptocurrency data from CoinGecko
5. The API server stores the data in MongoDB
6. Users can retrieve the latest statistics or price deviation via REST APIs

## API Endpoints

### Get Latest Statistics
```
GET /stats?coin=bitcoin
```
Returns the latest price, market cap, and 24-hour change percentage for the specified cryptocurrency.

### Get Price Deviation
```
GET /deviation?coin=bitcoin
```
Returns the standard deviation of price for the last 100 records of the specified cryptocurrency.

## Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- MongoDB
- NATS Server

### Installation

1. **Clone the repository**
   ```
   git clone <repository-url>
   cd cryptocurrency-stats
   ```

2. **Set up the API Server**
   ```
   cd api-server
   npm install
   cp .env.example .env
   # Edit .env to set your configuration
   npm start
   ```

3. **Set up the Worker Server**
   ```
   cd ../worker-server
   npm install
   cp .env.example .env
   # Edit .env to set your configuration
   npm start
   ```

## Optional Deployment

### MongoDB Atlas
1. Create a free MongoDB Atlas account
2. Set up a new cluster
3. Get your connection string
4. Update the `MONGODB_URI` in the API server's `.env` file

### Cloud Deployment
1. Create accounts on your preferred cloud provider (AWS, GCP, Azure, or Heroku)
2. Deploy each server following the platform-specific instructions
3. Set up environment variables
4. Ensure both servers can access the NATS server and MongoDB


# Cryptocurrency Dashboard Frontend

This is a Streamlit application that provides a user-friendly interface to interact with the cryptocurrency statistics API.

## Features

- Real-time cryptocurrency statistics display
- Price deviation visualization
- Interactive server management
- Automated server startup from the UI

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
   ```
   pip install streamlit pandas requests plotly
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Use the "Server Management" tab to start the API and worker servers

4. Once servers are running, switch to the "Dashboard" tab to view cryptocurrency data

## Components

The app consists of two main tabs:

1. **Dashboard Tab**
   - Displays real-time cryptocurrency statistics
   - Shows price, market cap, and 24-hour change
   - Visualizes price deviation data
   - Allows manual data refresh

2. **Server Management Tab**
   - Start/stop API and worker servers
   - View server logs
   - Server status indicators
   - Project documentation

## Architecture

The frontend communicates with the API server, which fetches data from CoinGecko and stores it in MongoDB. The worker server triggers periodic updates.

```
+----------------+       +--------------+       +-------------+       +---------+
| Streamlit UI   | <---> | API Server   | <---> | MongoDB     |       | CoinGecko |
| (app.py)       |       | (Node.js)    | <---> | Database    |  <--> | API      |
+----------------+       +--------------+       +-------------+       +---------+
                               ^
                               |
                         +-------------+
                         | Worker      |
                         | Server      |
                         | (Node.js)   |
                         +-------------+
```

## Dependencies

- streamlit
- pandas
- requests
- plotly
- subprocess (for server management)
- threading (for non-blocking process output)