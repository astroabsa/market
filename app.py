import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & 3-MINUTE AUTO-REFRESH
st.set_page_config(page_title="Live Market Feed", layout="centered", page_icon="📡")
st_autorefresh(interval=180000, key="news_refresh")

# 2. CUSTOM CSS FOR SINGLE COLUMN SCROLLER
st.markdown("""
    <style>
    .news-card {
        padding: 20px;
        border-radius: 12px;
        background-color: #00000;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 15px;
    }
    .category-tag {
        color: #ff4b4b;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 1px;
    }
    .timestamp {
        color: #888;
        font-size: 0.8rem;
        float: right;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA FETCHING FUNCTION
def get_all_news():
    feeds = {
        "NSE/BSE": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
        "MCX/CRUDE": "https://economictimes.indiatimes.com/markets/commodities/rssfeeds/2146844.cms",
        "GLOBAL/IRAN": "https://www.investing.com/rss/news_1.rss",
        "CRYPTO": "https://cointelegraph.com/rss"
    }
    
    combined_list = []
    for category, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                # Attempt to parse time, fallback to 'now' if missing
                published = entry.get('published', datetime.now().strftime("%H:%M:%S"))
                combined_list.append({
                    "category": category,
                    "title": entry.title,
                    "link": entry.link,
                    "time": published
                })
        except:
            continue
    return combined_list

# 4. UI DISPLAY
st.title("📡 Live Market Scanner")
st.caption(f"Last Refreshed: {datetime.now().strftime('%H:%M:%S')} | Updates every 3 mins")

news_data = get_all_news()

if not news_data:
    st.error("No news found. Checking connections...")
else:
    # Displaying as a vertical scroller
    for item in news_data:
        with st.container():
            st.markdown(f"""
                <div class="news-card">
                    <span class="category-tag">{item['category']}</span>
                    <span class="timestamp">{item['time']}</span>
                    <h3 style="margin-top:10px; font-size:1.1rem;">{item['title']}</h3>
                    <a href="{item['link']}" target="_blank" style="text-decoration:none; color:#4ea5ff;">Read Full Impact →</a>
                </div>
            """, unsafe_allow_html=True)

# Sidebar Manual Refresh
if st.sidebar.button("↻ Refresh Now"):
    st.rerun()
