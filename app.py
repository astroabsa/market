import streamlit as st
import feedparser
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. SETUP & 3-MINUTE AUTO-REFRESH
st.set_page_config(page_title="Pro Market Impact Scanner", layout="centered", page_icon="📡")
st_autorefresh(interval=180000, key="news_refresh")

# 2. INITIALIZE TOOLS
IST = pytz.timezone('Asia/Kolkata')
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    text_upper = text.upper()
    score = analyzer.polarity_scores(text)['compound']
    
    # 2026 Specific Impact Keywords (Iran War, FII Outflows)
    if any(word in text_upper for word in ["WAR", "STRIKE", "FII SELL", "RUPEE FALL", "CRUDE SPIKE"]):
        return "BEARISH 🔴"
    if any(word in text_upper for word in ["SURGE", "RALLY", "FII BUY", "STIMULUS", "GDP BEAT"]):
        return "BULLISH 🟢"
        
    if score >= 0.05: return "BULLISH 🟢"
    elif score <= -0.05: return "BEARISH 🔴"
    else: return "NEUTRAL ⚪"

def format_to_ist(struct_time):
    dt = datetime(*struct_time[:6], tzinfo=pytz.utc)
    return dt.astimezone(IST)

# 3. UI STYLING (Forced Contrast for Dark Mode)
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .news-card {
        padding: 18px;
        border-radius: 10px;
        background-color: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 12px;
    }
    .headline-text {
        color: #f0f6fc !important;
        margin: 10px 0;
        font-size: 1.05rem;
        line-height: 1.4;
        font-weight: 600;
    }
    .tag-container { display: flex; justify-content: space-between; margin-bottom: 10px; }
    .category-tag { color: #58a6ff; font-size: 0.7rem; font-weight: bold; border: 1px solid #58a6ff; padding: 2px 5px; border-radius: 3px; }
    .impact-tag { font-size: 0.75rem; font-weight: bold; padding: 2px 8px; border-radius: 4px; background: #21262d; }
    .timestamp { color: #8b949e; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# 4. DATA FETCHING (Verified 2026 Sources)
def fetch_all_feeds():
    # Swapped broken media links for official exchange & high-speed global feeds
    feeds = {
        "🇮🇳 NSE CORPORATE": "https://www.nseindia.com/static/rss/corporate_announcements.xml",
        "📊 INDIA MARKETS": "https://in.investing.com/rss/news_301.rss",
        "🔥 MCX/ENERGY": "https://in.investing.com/rss/news_11.rss",
        "💎 GOLD/BULLION": "https://www.kitco.com/rss/index.xml",
        "🌍 GLOBAL MACRO": "https://in.investing.com/rss/news_1.rss",
        "₿ CRYPTO": "https://cointelegraph.com/rss"
    }
    
    combined = []
    now_ist = datetime.now(IST)

    for cat, url in feeds.items():
        try:
            f = feedparser.parse(url)
            for entry in f.entries[:10]:
                dt_ist = format_to_ist(entry.published_parsed) if hasattr(entry, 'published_parsed') else now_ist
                impact = get_sentiment(entry.title)
                
                combined.append({
                    "cat": cat, "title": entry.title, "link": entry.link,
                    "time": dt_ist.strftime("%I:%M %p"), "raw_time": dt_ist, "impact": impact
                })
        except: continue
    
    combined.sort(key=lambda x: x['raw_time'], reverse=True)
    return combined

# 5. DASHBOARD
st.title("🛡️ Multi-Asset Real-Time Scanner")
st.caption(f"Tracking NSE, MCX & Crypto | Live IST: {datetime.now(IST).strftime('%I:%M:%S %p')}")

news_list = fetch_all_feeds()

if not news_list:
    st.error("Connection failed. Check your internet or Streamlit Cloud logs.")
else:
    for item in news_list:
        # High-Alert border for Bearish news (Crude spikes/War risk)
        alert = "2px solid #ff4b4b" if "BEARISH" in item['impact'] else "1px solid #30363d"
        
        st.markdown(f"""
            <div class="news-card" style="border-left: 5px solid {alert if '5px' in alert else alert}; border: {alert};">
                <div class="tag-container">
                    <span class="category-tag">{item['cat']}</span>
                    <span class="impact-tag">{item['impact']}</span>
                </div>
                <div class="headline-text">{item['title']}</div>
                <div style="margin-top: 12px;">
                    <span class="timestamp">🕒 {item['time']}</span>
                    <span style="float:right;"><a href="{item['link']}" target="_blank" style="color:#58a6ff; text-decoration:none; font-size:0.8rem;">Read Full Impact →</a></span>
                </div>
            </div>
        """, unsafe_allow_html=True)

if st.sidebar.button("↻ Refresh Feed"):
    st.rerun()
