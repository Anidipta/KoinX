# KoinX - Cryptocurrency Statistics System

## Just run app.py (Auto API Running Enabled)

This project consists of two Node.js servers that work together to collect, store, and expose cryptocurrency statistics and  a Streamlit application that provides a user-friendly interface to interact with the cryptocurrency statistics API.

## Demo Video

Download and watch the demo video here:  
[demo.mp4](demo.mp4)

## Features

- Real-time cryptocurrency statistics display
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
   - Shows price, market cap, and 24-hour change (Future)
   - Visualizes price deviation data (Future)
   - Allows manual data refresh

2. **Server Management Tab**
   - Start/stop API and worker servers
   - View server logs (Future)
   - Server status indicators 
   - Project documentation

## Architecture

The frontend communicates with the API server, which fetches data from CoinGecko and stores it in MongoDB. The worker server triggers periodic updates.

```
+----------------+       +--------------+       +-------------+       +---------------+
| Streamlit UI   | <---> | API Server   | <---> | MongoDB     |       | CoinGecko API | 
| (app.py)       |       |  (Python)    | <---> | Database    |  <--> |               |
+----------------+       +--------------+       +-------------+       +---------------+
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
