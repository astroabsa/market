import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & AUTO-REFRESH (Set to 180,000 milliseconds = 3 minutes)
st.set_page_config(page_title="Market Scanner Live", layout="wide", page_icon="📈")

count = st_autorefresh(interval=180000, limit=None, key="fscounter")

# 2. CSS FOR STYLING
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .news-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30333d;
        margin-bottom: 10px;
    }
    .market-tag {
        font-size: 0.8rem;
        padding: 2px 8px;
        border-radius: 5px;
        background: #1e2129;
    }
    </style>
    """, unsafe_allow_input=True)

# 3. DATA FETCHING LOGIC
def fetch_market_news(url, market_label):
    try:
        feed = feedparser.parse(url)
        entries = []
        for entry in feed.entries[:8]: # Get top 8 from each source
            entries.append({
                "Source": market_label,
                "Title": entry.title,
                "Link": entry.link,
                "Time": datetime.now().strftime("%H:%M:%S") # Timestamp of refresh
            })
        return entries
    except Exception as e:
        return []

# 4. DASHBOARD UI
st.title("📊 Multi-Market Live Scanner")
st.caption(f"Last updated at: {datetime.now().strftime('%H:%M:%S')} (Auto-refreshes every 3 mins)")

# Define your RSS Feeds
FEEDS = {
    "NSE/BSE (Stocks)": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "MCX (Commodities)": "https://www.business-standard.com/rss/markets-106.rss",
    "Crypto": "https://cointelegraph.com/rss"
}

# Layout: 3 Columns for 3 Markets
col1, col2, col3 = st.columns(3)

with col1:
    st.header("🇮🇳 NSE / BSE")
    nse_news = fetch_market_news(FEEDS["NSE/BSE (Stocks)"], "EQUITY")
    for item in nse_news:
        with st.container():
            st.markdown(f"**{item['Title']}**")
            st.caption(f"[{item['Source']}] • [Read More]({item['Link']})")
            st.divider()

with col2:
    st.header("🏗️ MCX")
    mcx_news = fetch_market_news(FEEDS["MCX (Commodities)"], "COMMODITY")
    for item in mcx_news:
        with st.container():
            st.markdown(f"**{item['Title']}**")
            st.caption(f"[{item['Source']}] • [Read More]({item['Link']})")
            st.divider()

with col3:
    st.header("₿ Crypto")
    crypto_news = fetch_market_news(FEEDS["Crypto"], "CRYPTO")
    for item in crypto_news:
        with st.container():
            st.markdown(f"**{item['Title']}**")
            st.caption(f"[{item['Source']}] • [Read More]({item['Link']})")
            st.divider()

# Sidebar for manual controls
st.sidebar.title("Scanner Stats")
st.sidebar.write(f"Refreshes completed: {count}")
if st.sidebar.button("Force Refresh Now"):
    st.rerun()
