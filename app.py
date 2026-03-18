import streamlit as st
import feedparser
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & 3-MINUTE AUTO-REFRESH
st.set_page_config(page_title="IST Market Feed", layout="centered", page_icon="📡")
st_autorefresh(interval=180000, key="news_refresh")

# 2. TIMEZONE CONFIG (IST)
IST = pytz.timezone('Asia/Kolkata')

def format_to_ist(struct_time):
    # Converts RSS struct_time to IST Datetime
    dt = datetime(*struct_time[:6], tzinfo=pytz.utc)
    return dt.astimezone(IST)

# 3. CUSTOM CSS
st.markdown("""
    <style>
    .news-card {
        padding: 18px;
        border-radius: 10px;
        background-color: #1e2129;
        border-left: 5px solid #00d4ff;
        margin-bottom: 12px;
    }
    .category-tag {
        color: #00d4ff;
        font-weight: bold;
        font-size: 0.7rem;
        letter-spacing: 1px;
    }
    .timestamp {
        color: #999;
        font-size: 0.75rem;
        float: right;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. DATA FETCHING
def get_all_news():
    feeds = {
        "NSE/BSE": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
        "MCX/CRUDE": "https://economictimes.indiatimes.com/markets/commodities/rssfeeds/2146844.cms",
        "GLOBAL/IRAN": "https://www.investing.com/rss/news_1.rss",
        "CRYPTO": "https://cointelegraph.com/rss"
    }
    
    combined_list = []
    now = datetime.now(IST)

    for category, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                # Convert published time to IST
                if hasattr(entry, 'published_parsed'):
                    dt_ist = format_to_ist(entry.published_parsed)
                    time_display = dt_ist.strftime("%I:%M %p")
                else:
                    time_display = now.strftime("%I:%M %p")
                
                combined_list.append({
                    "category": category,
                    "title": entry.title,
                    "link": entry.link,
                    "time": time_display,
                    "raw_time": dt_ist if hasattr(entry, 'published_parsed') else now
                })
        except:
            continue
    
    # Sort by newest first
    combined_list.sort(key=lambda x: x['raw_time'], reverse=True)
    return combined_list

# 5. UI DISPLAY
st.title("📡 Live IST Market Scanner")
st.write(f"**Current Time (IST):** {datetime.now(IST).strftime('%Y-%m-%d | %I:%M:%S %p')}")

news_data = get_all_news()

if not news_data:
    st.warning("Fetching live updates...")
else:
    for item in news_data:
        with st.container():
            st.markdown(f"""
                <div class="news-card">
                    <span class="category-tag">{item['category']}</span>
                    <span class="timestamp">🕒 {item['time']}</span>
                    <h3 style="margin-top:8px; font-size:1rem; color:#f0f2f6;">{item['title']}</h3>
                    <a href="{item['link']}" target="_blank" style="text-decoration:none; color:#00d4ff; font-size:0.8rem;">Read Analysis →</a>
                </div>
            """, unsafe_allow_html=True)

# Manual Refresh in Sidebar
if st.sidebar.button("↻ Force Refresh"):
    st.rerun()
