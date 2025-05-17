import streamlit as st
import requests
import pandas as pd
import time
import json
import subprocess
import os
import threading
import plotly.graph_objects as go
from datetime import datetime
import plotly.express as px

# Global variables
API_URL = "http://localhost:3000"
SUPPORTED_COINS = ["bitcoin", "ethereum", "matic-network"]
COIN_NAMES = {"bitcoin": "Bitcoin", "ethereum": "Ethereum", "matic-network": "Polygon (Matic)"}
COIN_ICONS = {
    "bitcoin": "₿",
    "ethereum": "Ξ",
    "matic-network": "⬡"
}

def run_server_process(server_type):
    """Run API or Worker server in background"""
    try:
        if server_type == "api":
            st.session_state.api_output = ""
            process = subprocess.Popen(
                ["npm", "install", "&&", "npm", "start"], 
                cwd="./api-server",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            st.session_state.api_process = process
            
        elif server_type == "worker":
            st.session_state.worker_output = ""
            process = subprocess.Popen(
                ["npm", "install", "&&", "npm", "start"],
                cwd="./worker-server",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            st.session_state.worker_process = process
            
        # Start a thread to capture process output
        threading.Thread(
            target=capture_process_output,
            args=(process, server_type),
            daemon=True
        ).start()
            
        return True
    except Exception as e:
        st.error(f"Failed to start {server_type} server: {str(e)}")
        return False

def capture_process_output(process, server_type):
    """Capture and store process output for display"""
    output_key = f"{server_type}_output"
    
    for line in process.stdout:
        if server_type == "api":
            st.session_state.api_output += line
        else:
            st.session_state.worker_output += line
            
def stop_server_process(server_type):
    """Stop API or Worker server process"""
    if server_type == "api" and hasattr(st.session_state, "api_process"):
        st.session_state.api_process.terminate()
        st.session_state.api_process = None
    elif server_type == "worker" and hasattr(st.session_state, "worker_process"):
        st.session_state.worker_process.terminate()
        st.session_state.worker_process = None

def check_api_health():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_coin_stats(coin):
    """Get statistics for a specific coin"""
    try:
        response = requests.get(f"{API_URL}/stats", params={"coin": coin}, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching stats: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def get_coin_deviation(coin):
    """Get price deviation for a specific coin"""
    try:
        response = requests.get(f"{API_URL}/deviation", params={"coin": coin}, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching deviation: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def trigger_update():
    """Manually trigger crypto stats update"""
    try:
        response = requests.post(f"{API_URL}/trigger-update")
        if response.status_code == 200:
            st.success("Cryptocurrency stats updated successfully!")
            return True
        else:
            st.error(f"Failed to update stats: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def create_price_card(coin, stats):
    """Create a styled card for coin price data"""
    if not stats:
        return
    
    price = stats.get("price", 0)
    market_cap = stats.get("marketCap", 0)
    change_24h = stats.get("24hChange", 0)
    
    # Format values
    price_formatted = f"${price:,.2f}"
    market_cap_formatted = f"${market_cap:,.0f}"
    
    # Set color based on 24h change
    color = "green" if change_24h >= 0 else "red"
    change_icon = "↑" if change_24h >= 0 else "↓"
    
    # Create card
    with st.container():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"""
            <div style="font-size:52px; text-align:center; padding:10px;">
                {COIN_ICONS[coin]}
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div style="background-color:#1E1E1E; border-radius:10px; padding:15px; margin-bottom:10px;">
                <h3 style="margin:0; color:white;">{COIN_NAMES[coin]}</h3>
                <div style="font-size:24px; font-weight:bold; margin:5px 0;">{price_formatted}</div>
                <div style="display:flex; justify-content:space-between;">
                    <span>Market Cap: {market_cap_formatted}</span>
                    <span style="color:{color};">{change_icon} {abs(change_24h):.2f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_readme():
    """Display project README information"""
    st.markdown("""
    # Cryptocurrency Statistics System
    
    This application displays real-time cryptocurrency statistics by fetching data from a custom API that collects data from CoinGecko.
    
    ## Architecture
    
    The system consists of three main components:
    
    1. **Frontend (Streamlit)**: This web interface you're using now
    2. **API Server**: Node.js server that provides endpoints for cryptocurrency data
    3. **Worker Server**: Background service that triggers data updates every 15 minutes
    
    ## Features
    
    - Real-time price, market cap, and 24-hour change display
    - Price deviation calculations
    - Manual data refresh
    - Server management interface
    
    ## How It Works
    
    1. The worker server triggers an update every 15 minutes via NATS
    2. The API server receives this event and fetches new data from CoinGecko
    3. Data is stored in MongoDB for historical analysis
    4. This frontend displays the data through API calls
    
    ## Getting Started
    
    Navigate to the "Server Management" tab to start the API and worker servers.
    """)

def init_session_state():
    """Initialize session state variables"""
    if "api_process" not in st.session_state:
        st.session_state.api_process = None
    if "worker_process" not in st.session_state:
        st.session_state.worker_process = None
    if "api_output" not in st.session_state:
        st.session_state.api_output = ""
    if "worker_output" not in st.session_state:
        st.session_state.worker_output = ""
    if "last_update" not in st.session_state:
        st.session_state.last_update = None

def main():
    # Set page config
    st.set_page_config(
        page_title="Crypto Stats Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #0E1117;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #262730;
            border-bottom: 2px solid #4CAF50;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0px;
        }
        div[data-testid="stMetric"] {
            background-color: #1E1E1E;
            border-radius: 5px;
            padding: 10px;
        }
        section[data-testid="stSidebar"] button {
            width: 100%;
            margin-bottom: 10px;
        }
        .server-status {
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
            display: inline-block;
        }
        .server-status.online {
            background-color: #4CAF50;
            color: white;
        }
        .server-status.offline {
            background-color: #F44336;
            color: white;
        }
        .css-1avcm0n {
            height: 40px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # App title
    st.title("📊 Crypto Stats Dashboard")
    
    # Create tabs
    tab1, tab2 = st.tabs(["📈 Dashboard", "⚙️ Server Management"])
    
    # Dashboard tab
    with tab1:
        # Check if API is available
        api_available = check_api_health()
        
        if not api_available:
            st.warning("API server is not available. Please go to Server Management tab to start the servers.")
        else:
            st.success("Connected to API server successfully!")
            
            # Add refresh button and last update time
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔄 Refresh Data"):
                    if trigger_update():
                        st.session_state.last_update = datetime.now()
            
            with col3:
                if st.session_state.last_update:
                    st.text(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
            
            # Display coin data
            st.subheader("Cryptocurrency Prices")
            for coin in SUPPORTED_COINS:
                stats = get_coin_stats(coin)
                create_price_card(coin, stats)
            
            # Create deviation section
            st.subheader("Price Deviation Analysis")
            st.write("Standard deviation of price for the last 100 records:")
            
            deviation_data = {}
            
            for coin in SUPPORTED_COINS:
                deviation_result = get_coin_deviation(coin)
                if deviation_result:
                    deviation_data[coin] = deviation_result.get("deviation", 0)
            
            if deviation_data:
                # Create bar chart for deviations
                fig = px.bar(
                    x=list(deviation_data.keys()),
                    y=list(deviation_data.values()),
                    color=list(deviation_data.values()),
                    labels={"x": "Cryptocurrency", "y": "Standard Deviation (USD)"},
                    text=[f"{val:.2f}" for val in deviation_data.values()],
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(
                    title="Price Volatility Comparison",
                    xaxis_title="",
                    yaxis_title="Standard Deviation (USD)",
                    showlegend=False,
                    height=400
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                
                # Update x-axis labels to full names
                fig.update_xaxes(
                    ticktext=[COIN_NAMES[coin] for coin in deviation_data.keys()],
                    tickvals=list(deviation_data.keys())
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
    # Server Management tab
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("API Server")
            
            api_status = "online" if check_api_health() else "offline"
            st.markdown(f"""
            <div>Status: <span class="server-status {api_status}">{api_status.upper()}</span></div>
            """, unsafe_allow_html=True)
            
            if not check_api_health():
                if st.button("Start API Server"):
                    run_server_process("api")
                    st.success("Starting API server... Please wait")
            else:
                if st.button("Stop API Server"):
                    stop_server_process("api")
                    st.warning("Stopping API server...")
            
            st.subheader("Server Output")
            st.code(st.session_state.api_output, language="bash")
        
        with col2:
            st.header("Worker Server")
            
            # We don't have a direct health check for worker server
            worker_running = hasattr(st.session_state, "worker_process") and st.session_state.worker_process is not None
            worker_status = "online" if worker_running else "offline"
            
            st.markdown(f"""
            <div>Status: <span class="server-status {worker_status}">{worker_status.upper()}</span></div>
            """, unsafe_allow_html=True)
            
            if not worker_running:
                if st.button("Start Worker Server"):
                    run_server_process("worker")
                    st.success("Starting Worker server... Please wait")
            else:
                if st.button("Stop Worker Server"):
                    stop_server_process("worker")
                    st.warning("Stopping Worker server...")
            
            st.subheader("Server Output")
            st.code(st.session_state.worker_output, language="bash")
        
        st.divider()
        display_readme()

if __name__ == "__main__":
    main()