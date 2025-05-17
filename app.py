import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import json
import subprocess
import os
import threading
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from io import BytesIO
import base64

# Global variables
API_URL = "http://localhost:3000"
SUPPORTED_COINS = ["bitcoin", "ethereum", "matic-network"]
COIN_NAMES = {
    "bitcoin": "Bitcoin", 
    "ethereum": "Ethereum", 
    "matic-network": "Polygon (Matic)"
}
COIN_ICONS = {
    "bitcoin": "₿",
    "ethereum": "Ξ",
    "matic-network": "⬡"
}
COIN_COLORS = {
    "bitcoin": "#F7931A",
    "ethereum": "#627EEA",
    "matic-network": "#8247E5"
}

# Initialize session state
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
    if "selected_coins" not in st.session_state:
        st.session_state.selected_coins = ["bitcoin", "ethereum"]
    if "price_history" not in st.session_state:
        st.session_state.price_history = {}
    if "time_range" not in st.session_state:
        st.session_state.time_range = "24h"
    if "notifications" not in st.session_state:
        st.session_state.notifications = []
    if "alert_thresholds" not in st.session_state:
        st.session_state.alert_thresholds = {coin: {"upper": None, "lower": None} for coin in SUPPORTED_COINS}
    if "display_mode" not in st.session_state:
        st.session_state.display_mode = "cards"  # Options: cards, table, minimal

# Server management functions
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

# API interaction functions
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

def get_market_dominance():
    """Get market dominance data for top cryptocurrencies"""
    try:
        response = requests.get(f"{API_URL}/market-dominance", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching market dominance: {response.text}")
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

def set_price_alert(coin, upper=None, lower=None):
    """Set price alerts for a specific coin"""
    try:
        data = {
            "coin": coin,
            "upperThreshold": upper,
            "lowerThreshold": lower
        }
        response = requests.post(f"{API_URL}/set-alert", json=data, timeout=5)
        if response.status_code == 200:
            st.success(f"Price alert set for {COIN_NAMES[coin]}")
            # Update session state
            st.session_state.alert_thresholds[coin] = {"upper": upper, "lower": lower}
            return True
        else:
            st.error(f"Failed to set price alert: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def check_price_alerts():
    """Check if any price alerts have been triggered"""
    try:
        response = requests.get(f"{API_URL}/check-alerts", timeout=5)
        if response.status_code == 200:
            alerts = response.json()
            if alerts and len(alerts) > 0:
                for alert in alerts:
                    # Add to notifications if not already there
                    if alert not in st.session_state.notifications:
                        st.session_state.notifications.append(alert)
                return alerts
            return []
        else:
            return []
    except:
        return []

# UI Component functions
def create_price_card(coin, stats):
    """Create a styled card for coin price data"""
    if not stats:
        return
    
    price = stats.get("price", 0)
    market_cap = stats.get("marketCap", 0)
    change_24h = stats.get("24hChange", 0)
    volume_24h = stats.get("24hVolume", 0)
    
    # Format values
    price_formatted = f"${price:,.2f}"
    market_cap_formatted = f"${market_cap:,.0f}"
    volume_formatted = f"${volume_24h:,.0f}"
    
    # Set color based on 24h change
    color = "green" if change_24h >= 0 else "red"
    change_icon = "↑" if change_24h >= 0 else "↓"
    
    # Create card
    with st.container():
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown(f"""
            <div style="font-size:52px; text-align:center; padding:10px; color:{COIN_COLORS[coin]}">
                {COIN_ICONS[coin]}
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div style="background-color:#1E1E1E; border-radius:10px; padding:15px; margin-bottom:15px;">
                <h3 style="margin:0; color:white;">{COIN_NAMES[coin]}</h3>
                <div style="font-size:24px; font-weight:bold; margin:5px 0;">{price_formatted}</div>
                <div style="display:flex; justify-content:space-between;">
                    <span>Market Cap: {market_cap_formatted}</span>
                    <span style="color:{color};">{change_icon} {abs(change_24h):.2f}%</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:5px;">
                    <span>24h Volume: {volume_formatted}</span>
                    <span>Rank: #{stats.get('marketCapRank', 'N/A')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def create_price_table(coins_data):
    """Create a table view of all coin data"""
    if not coins_data:
        return
        
    # Prepare data for table
    data = []
    for coin, stats in coins_data.items():
        if stats:
            data.append({
                "Coin": COIN_NAMES[coin],
                "Icon": COIN_ICONS[coin],
                "Price (USD)": stats.get("price", 0),
                "24h Change": stats.get("24hChange", 0),
                "Market Cap": stats.get("marketCap", 0),
                "24h Volume": stats.get("24hVolume", 0),
                "Rank": stats.get("marketCapRank", "N/A")
            })
    
    if not data:
        return
        
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Style function for the dataframe
    def style_negative_red(v):
        return f"color: {'red' if v < 0 else 'green'}"
        
    # Apply styling
    styled_df = df.style.format({
        "Price (USD)": "${:.2f}",
        "24h Change": "{:.2f}%",
        "Market Cap": "${:,.0f}",
        "24h Volume": "${:,.0f}"
    }).applymap(style_negative_red, subset=["24h Change"])
    
    st.dataframe(styled_df, use_container_width=True)

def create_minimal_view(coins_data):
    """Create a minimal ticker-style view of coin prices"""
    if not coins_data:
        return
        
    # Create a horizontal list of coins with minimal info
    col_count = min(len(coins_data), 3)  # Use at most 3 columns
    cols = st.columns(col_count)
    
    idx = 0
    for coin, stats in coins_data.items():
        if stats:
            price = stats.get("price", 0)
            change_24h = stats.get("24hChange", 0)
            
            color = "green" if change_24h >= 0 else "red"
            change_icon = "↑" if change_24h >= 0 else "↓"
            
            with cols[idx % col_count]:
                st.markdown(f"""
                <div style="background-color:#1E1E1E; border-radius:5px; padding:8px; margin:5px 0; text-align:center;">
                    <span style="color:{COIN_COLORS[coin]}; font-size:18px;">{COIN_ICONS[coin]}</span>
                    <span style="font-weight:bold; margin-left:5px;">{COIN_NAMES[coin]}</span>
                    <div style="font-size:16px;">${price:,.2f}</div>
                    <div style="color:{color}; font-size:14px;">{change_icon} {abs(change_24h):.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            idx += 1

def display_price_alerts_section():
    """Display and manage price alerts"""
    st.subheader("Price Alerts")
    
    with st.expander("Set Price Alerts", expanded=False):
        # Allow user to set price alerts
        col1, col2 = st.columns(2)
        
        with col1:
            alert_coin = st.selectbox("Select Cryptocurrency", 
                options=SUPPORTED_COINS,
                format_func=lambda x: COIN_NAMES[x])
        
        with col2:
            current_price = None
            stats = get_coin_stats(alert_coin)
            if stats:
                current_price = stats.get("price", 0)
                st.info(f"Current price: ${current_price:,.2f}")
        
        if current_price:
            col1, col2 = st.columns(2)
            
            with col1:
                upper_threshold = st.number_input(
                    "Upper Price Threshold ($)",
                    min_value=0.0,
                    value=float(current_price * 1.05),  # Default 5% above
                    step=0.01,
                    format="%.2f"
                )
            
            with col2:
                lower_threshold = st.number_input(
                    "Lower Price Threshold ($)",
                    min_value=0.0,
                    value=float(current_price * 0.95),  # Default 5% below
                    step=0.01,
                    format="%.2f"
                )
            
            if st.button("Set Alert"):
                set_price_alert(alert_coin, upper_threshold, lower_threshold)
    
    # Display active alerts
    active_alerts = {coin: thresholds for coin, thresholds in st.session_state.alert_thresholds.items() 
                    if thresholds["upper"] is not None or thresholds["lower"] is not None}
    
    if active_alerts:
        st.subheader("Active Alerts")
        
        for coin, thresholds in active_alerts.items():
            upper = thresholds["upper"]
            lower = thresholds["lower"]
            
            if upper is not None or lower is not None:
                with st.container():
                    st.markdown(f"""
                    <div style="background-color:#1E1E1E; border-radius:5px; padding:10px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between;margin-top:20px;">
                            <span>{COIN_NAMES[coin]} ({COIN_ICONS[coin]})</span>
                            <button style="background:none; border:none; color:red; cursor:pointer;">✕</button>
                        </div>
                        <div style="margin-top:5px;">
                            {f"Upper: ${upper:,.2f}" if upper is not None else ""}
                            {" | " if upper is not None and lower is not None else ""}
                            {f"Lower: ${lower:,.2f}" if lower is not None else ""}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Display notifications
    if st.session_state.notifications:
        st.subheader("Alert Notifications")
        
        for notification in st.session_state.notifications:
            coin = notification.get("coin", "")
            price = notification.get("price", 0)
            threshold = notification.get("threshold", 0)
            alert_type = notification.get("type", "")
            
            color = "green" if alert_type == "upper" else "red"
            icon = "↑" if alert_type == "upper" else "↓"
            
            st.markdown(f"""
            <div style="background-color:#1E1E1E; border-radius:5px; padding:10px; margin-bottom:10px; border-left:4px solid {color};">
                <div style="font-weight:bold;">{COIN_NAMES.get(coin, coin)} Price Alert</div>
                <div>
                    Current price: ${price:,.2f} {icon} 
                    <span style="color:{color};">{threshold_text}</span>
                </div>
                <div style="font-size:12px; color:#888;">
                    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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
    - Interactive price history charts with volume data
    - Market dominance visualization
    - Price correlation analysis
    - Trading volume comparisons
    - Price deviation calculations
    - Customizable price alerts
    - Multiple display modes: cards, table, and minimal
    - Manual data refresh
    - Server management interface
    
    ## How It Works
    
    1. The worker server triggers an update every 15 minutes via NATS messaging system
    2. The API server receives this event and fetches new data from CoinGecko
    3. Data is stored in MongoDB for historical analysis
    4. This frontend displays the data through API calls
    
    ## Getting Started
    
    Navigate to the "Server Management" tab to start the API and worker servers. Once the servers are running,
    you can use the dashboard to view and analyze cryptocurrency data.
    
    ## Supported Cryptocurrencies
    
    Currently, the system supports the following cryptocurrencies:
    
    - Bitcoin (BTC)
    - Ethereum (ETH)
    - Polygon (MATIC)
    
    ## API Endpoints
    
    - `/health` - API health check
    - `/stats` - Get current statistics for a specific coin
    - `/set-alert` - Set price alerts
    - `/trigger-update` - Manually trigger a data update
    """)

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
        /* Center headers */
        h1, h2, h3, h4, h5, h6 {
            text-align: center;
            margin-bottom:20px;
        }
        
        /* Tabs styling with full width */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            width: 100%;
            display: flex;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #0E1117;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            flex-grow: 1;
            text-align: center;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #262730;
            border-bottom: 2px solid #4CAF50;
        }
        
        /* Remove gap between vertical blocks */
        div[data-testid="stVerticalBlock"] {
            gap: 0px;
        }
        
        /* Metric styling */
        div[data-testid="stMetric"] {
            background-color: #1E1E1E;
            border-radius: 5px;
            padding: 10px;
        }
        
        /* Sidebar buttons */
        section[data-testid="stSidebar"] button {
            width: 100%;
            margin-bottom: 10px;
            display: flex;
            justify-content: center;
        }
        
        /* Server status indicators */
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
        
        /* Header height */
        .css-1avcm0n {
            height: 40px;
        }
        
        /* Expander styling */
        .stExpander {
            border: 1px solid #333;
            border-radius: 8px;
        }
        
        /* Custom notification area */
        .notification-badge {
            background-color: #f44336;
            color: white;
            border-radius: 50%;
            padding: 0.2rem 0.5rem;
            font-size: 0.8rem;
            position: absolute;
            top: -5px;
            right: -5px;
        }
        
        /* Improved metric cards with color options */
        .metric-card {
            background-color: #1E1E1E;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }
        
        .metric-card.green {
            border-left: 4px solid #4CAF50;
        }
        
        .metric-card.blue {
            border-left: 4px solid #2196F3;
        }
        
        .metric-card.purple {
            border-left: 4px solid #9C27B0;
        }
        
        .metric-card.orange {
            border-left: 4px solid #FF9800;
        }
        
        /* Custom toggle buttons */
        .view-toggle {
            display: inline-flex;
            overflow: hidden;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        
        .view-toggle label {
            padding: 8px 16px;
            background-color: #1E1E1E;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .view-toggle label:hover {
            background-color: #333;
        }
        
        .view-toggle input[type="radio"] {
            display: none;
        }
        
        .view-toggle input[type="radio"]:checked + label {
            background-color: #4CAF50;
            color: white;
        }
        
        /* Color theme options */
        .theme-primary {
            color: #4CAF50;
        }
        
        .theme-secondary {
            color: #2196F3;
        }
        
        .theme-accent {
            color: #FF9800;
        }
        
        .theme-warning {
            color: #FFC107;
        }
        
        .theme-error {
            color: #F44336;
        }
        
        .theme-info {
            color: #00BCD4;
        }
        
        /* Background color options for containers */
        .bg-dark {
            background-color: #1E1E1E;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .bg-darker {
            background-color: #121212;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .bg-highlight {
            background-color: #2A2A2A;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
    </style>
    """, unsafe_allow_html=True) 
    
    # App title and header
    st.title("📊 Crypto Stats Dashboard")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard", "📊 Analysis", "⚙️ Server Management", "ℹ️ About"])
    
    # Dashboard tab
    with tab1:
        # Check if API is available
        api_available = check_api_health()
        
        if not api_available:
            st.warning("API server is not available. Please go to Server Management tab to start the servers.")
        else:
            # Add refresh button and last update time
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔄 Refresh Data"):
                    if trigger_update():
                        st.session_state.last_update = datetime.now()
                        # Check for any price alerts
                        check_price_alerts()
            
            with col3:
                if st.session_state.last_update:
                    st.text(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
            
            # Display view options
            view_options = ["cards", "table", "minimal"]
            view_labels = {"cards": "Card View", "table": "Table View", "minimal": "Minimal View"}
            
            col1, col2 = st.columns([2, 3])
            with col1:
                st.session_state.display_mode = st.radio(
                    "Display Mode:",
                    options=view_options,
                    format_func=lambda x: view_labels[x],
                    horizontal=True,
                    key="display_mode_selector"
                )
            
            with col2:
                # Create multiselect for coins
                selected_coins = st.multiselect(
                    "Select cryptocurrencies to display:",
                    options=SUPPORTED_COINS,
                    default=st.session_state.selected_coins,
                    format_func=lambda x: COIN_NAMES[x]
                )
                
                if selected_coins:
                    st.session_state.selected_coins = selected_coins
            
            st.divider()
            
            # Display coin data based on selected display mode
            if st.session_state.selected_coins:
                # Fetch data for selected coins
                coins_data = {}
                for coin in st.session_state.selected_coins:
                    stats = get_coin_stats(coin)
                    if stats:
                        coins_data[coin] = stats
                
                # Display according to selected mode
                if st.session_state.display_mode == "cards":
                    for coin in st.session_state.selected_coins:
                        if coin in coins_data:
                            create_price_card(coin, coins_data[coin])
                
                elif st.session_state.display_mode == "table":
                    create_price_table(coins_data)
                
                else:  # minimal view
                    create_minimal_view(coins_data)
            
            # Display price alerts section
            display_price_alerts_section()
    
    # Analysis tab
    with tab2:
        if not api_available:
            st.warning("API server is not available. Please go to Server Management tab to start the servers.")
        else:
            st.header("Cryptocurrency Market Analysis")
            
            # Price deviation analysis
            st.subheader("Price Volatility Analysis")
            deviation_data = {}
            for coin in SUPPORTED_COINS:
                deviation_result = get_coin_deviation(coin)
                if deviation_result:
                    deviation_data[coin] = deviation_result.get("deviation", 0)
            
            if deviation_data:
                # Create bar chart for deviations
                fig = px.bar(
                    x=[COIN_NAMES[coin] for coin in deviation_data.keys()],
                    y=list(deviation_data.values()),
                    color=list(deviation_data.values()),
                    labels={"x": "Cryptocurrency", "y": "Standard Deviation (USD)"},
                    text=[f"${val:.2f}" for val in deviation_data.values()],
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(
                    title="Price Volatility Comparison",
                    xaxis_title="",
                    yaxis_title="Standard Deviation (USD)",
                    showlegend=False,
                    height=400,
                    template="plotly_dark"
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                
                st.plotly_chart(fig, use_container_width=True)
            
            
            
            
            # Trading volume trends
            st.subheader("Trading Volume Trends")
            
            # Mock volume trend data (in a real app, this would come from the API)
            trend_data = {}
            for coin in SUPPORTED_COINS:
                # Generate some mock data for visualization
                base_volume = {"bitcoin": 30, "ethereum": 20, "matic-network": 8, 
                               "solana": 15, "cardano": 5, "ripple": 10}[coin] * 1e9
                trend_data[coin] = [base_volume * (0.8 + 0.4 * np.random.random()) for _ in range(30)]
            
            # Create figure
            fig = go.Figure()
            
            for coin in SUPPORTED_COINS:
                fig.add_trace(go.Scatter(
                    x=list(range(1, 31)),
                    y=trend_data[coin],
                    mode='lines',
                    name=COIN_NAMES[coin],
                    line=dict(color=COIN_COLORS[coin], width=2)
                ))
            
            fig.update_layout(
                title="30-Day Trading Volume Trends",
                xaxis_title="Day",
                yaxis_title="Trading Volume (USD)",
                height=500,
                template="plotly_dark",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Format y-axis to show billions
            fig.update_yaxes(tickformat="$.2s")
            
            st.plotly_chart(fig, use_container_width=True)
            
    # Server Management tab
    with tab3:
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
                    time.sleep(3)
                    st.rerun()
            else:
                if st.button("Stop API Server"):
                    stop_server_process("api")
                    st.warning("Stopping API server...")
                    time.sleep(3)
                    st.rerun()
        
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
                    time.sleep(3)
                    st.rerun()
            else:
                if st.button("Stop Worker Server"):
                    stop_server_process("worker")
                    st.warning("Stopping Worker server...")
                    time.sleep(3)
                    st.rerun()
        
        st.divider()
        
        # Server configuration section
        st.header("Server Configuration")
        
        with st.expander("API Server Configuration", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("MongoDB URI", value="", key="mongo_uri")
                st.text_input("API Port", value="3000", key="api_port")
            
            with col2:
                st.text_input("NATS Server", value="nats://localhost:4222", key="nats_server")
                st.selectbox("Log Level", options=["debug", "info", "warn", "error"], index=1, key="api_log_level")
            
            if st.button("Save API Configuration"):
                st.success("API configuration saved successfully!")
        
        with st.expander("Worker Server Configuration", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("CoinGecko API Key", value="", key="coingecko_api_key", type="password")
                st.number_input("Update Interval (minutes)", min_value=1, max_value=60, value=15, key="update_interval")
            
            with col2:
                st.text_input("NATS Server", value="nats://localhost:4222", key="worker_nats_server")
                st.selectbox("Log Level", options=["debug", "info", "warn", "error"], index=1, key="worker_log_level")
            
            if st.button("Save Worker Configuration"):
                st.success("Worker configuration saved successfully!")
    
    # About tab
    with tab4:
        display_readme()
        
        # System metrics
        st.header("System Metrics")
        
        # Mock metrics for demo
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="API Uptime", value="12h 34m")
        with col2:
            st.metric(label="DB Size", value="154 MB")
        with col3:
            st.metric(label="API Requests", value="1,254")
        
        # Team/Contributors section
        st.header("Development Team")
        
        team_members = [
            {"name": "Anidipta Pall", "role": "Full Stack Developer+UI/UX", "avatar": "AP"}
        ]
        
        cols = st.columns(len(team_members))
        
        for i, member in enumerate(team_members):
            with cols[i]:
                st.markdown(f"""
                <div style="text-align:center; padding:10px;">
                    <div style="background-color:#4CAF50; color:white; width:60px; height:60px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:24px; margin-bottom:10px;">
                        {member["avatar"]}
                    </div>
                    <h4 style="margin:5px 0;">{member["name"]}</h4>
                    <div style="color:#888;">{member["role"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Version info
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("Version: 1.2.0")
        with col2:
            st.info("Last Updated: May 15, 2025")

if __name__ == "__main__":
    main()