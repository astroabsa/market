import streamlit as st
import feedparser
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & 3-MINUTE AUTO-REFRESH
st.set_page_config(page_title="Market War Room", layout="wide", page_icon="🌍")
st_autorefresh(interval=180000, key="datarefresh")

# 2. IMPROVED STYLING
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stExpander { border: 1px solid #ff4b4b; border-radius: 10px; margin-bottom: 10px; }
    .highlight { color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def fetch_news(url):
    try:
        feed = feedparser.parse(url)
        return feed.entries[:10]
    except:
        return []

# 3. GLOBAL & GEOPOLITICAL FEEDS
FEEDS = {
    "NSE_STOCKS": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "MCX_COMMODITIES": "https://economictimes.indiatimes.com/markets/commodities/rssfeeds/2146844.cms",
    "GEOPOLITICAL_RISK": "https://www.theguardian.com/world/iran/rss", # Tracking Iran specifically
    "CRYPTO": "https://cointelegraph.com/rss"
}

st.title("🛡️ Multi-Market War Room Scanner")
st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')} | Auto-refresh: 3 mins")

# 4. DASHBOARD LAYOUT
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🇮🇳 NSE / BSE News")
    for entry in fetch_news(FEEDS["NSE_STOCKS"]):
        with st.container():
            st.markdown(f"**{entry.title}**")
            st.caption(f"[Source: ET] • [Read]({entry.link})")
            st.divider()

with col2:
    st.subheader("🔥 MCX & Crude Impact")
    # Added a secondary fallback for MCX
    mcx_news = fetch_news(FEEDS["MCX_COMMODITIES"])
    if not mcx_news:
        st.warning("Primary MCX feed empty. Loading global energy news...")
        mcx_news = fetch_news("https://www.investing.com/rss/news_11.rss") # Energy News
        
    for entry in mcx_news:
        # Highlight news mentioning Crude or Iran
        title = entry.title
        if any(word in title.upper() for word in ["CRUDE", "OIL", "IRAN", "WAR"]):
            st.markdown(f"🚨 <span class='highlight'>{title}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**{title}**")
        st.caption(f"[Source: News] • [Read]({entry.link})")
        st.divider()

with col3:
    st.subheader("₿ Crypto & Global Risk")
    # Mixing Geopolitical news with Crypto
    geo_news = fetch_news(FEEDS["GEOPOLITICAL_RISK"])
    crypto_news = fetch_news(FEEDS["CRYPTO"])
    
    st.info("⚠️ Geopolitical Alert: Iran Conflict")
    for entry in geo_news[:3]: # Top 3 War updates
        st.markdown(f"🌍 *{entry.title}*")
        st.caption(f"[Geopolitics] • [Read]({entry.link})")
        
    st.markdown("---")
    for entry in crypto_news[:7]:
        st.markdown(f"**{entry.title}**")
        st.caption(f"[Crypto] • [Read]({entry.link})")
        st.divider()
