import streamlit as st
import feedparser
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. SETTINGS & REFRESH
st.set_page_config(page_title="Multi-Asset Scanner 2026", layout="centered")
st_autorefresh(interval=60000, key="news_refresh")
IST = pytz.timezone('Asia/Kolkata')
analyzer = SentimentIntensityAnalyzer()

# 2. VERIFIED 2026 MULTI-ASSET FEEDS
FEEDS = {
    "🇮🇳 NSE CORPORATE": "https://www.nseindia.com/static/rss/corporate_announcements.xml",
    "📊 INDIA MARKETS": "https://www.investing.com/rss/news_301.rss", # Dedicated India Feed
    "🔥 MCX/ENERGY": "https://www.investing.com/rss/news_11.rss",
    "💎 GOLD/BULLION": "https://www.kitco.com/rss/index.xml",
    "🌍 GLOBAL MACRO": "https://www.investing.com/rss/news_1.rss",
    "₿ CRYPTO": "https://cointelegraph.com/rss"
}

def get_impact(title):
    t = title.upper()
    score = analyzer.polarity_scores(title)['compound']
    # 2026 Specific Risk Keywords (Iran War, FII Outflow, Rate Hikes)
    if any(w in t for w in ["WAR", "IRAN", "STRIKE", "FII SELL", "RUPEE FALL"]): return "BEARISH 🔴"
    if any(w in t for w in ["RALLY", "FII BUY", "SURGE", "STIMULUS"]): return "BULLISH 🟢"
    return "NEUTRAL ⚪" if -0.05 < score < 0.05 else ("POSITIVE ⬆️" if score > 0 else "NEGATIVE ⬇️")

# 3. UI STYLING
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .news-card { padding: 18px; border-radius: 10px; background-color: #161b22; border: 1px solid #30363d; margin-bottom: 12px; }
    .headline { color: #f0f6fc !important; font-weight: 600; font-size: 1.05rem; }
    .meta { display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 10px; }
    .cat-tag { color: #58a6ff; font-weight: bold; border: 1px solid #58a6ff; padding: 2px 5px; border-radius: 3px; }
    .impact-tag { background: #21262d; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 4. DATA PROCESSING
all_news = []
for cat, url in FEEDS.items():
    try:
        f = feedparser.parse(url)
        for e in f.entries[:10]:
            # Improved Time Parsing for 2026 Feeds
            dt = datetime(*e.published_parsed[:6], tzinfo=pytz.utc).astimezone(IST) if hasattr(e, 'published_parsed') else datetime.now(IST)
            all_news.append({
                "cat": cat, "title": e.title, "link": e.link, 
                "time": dt.strftime("%I:%M %p"), "raw": dt, "impact": get_impact(e.title)
            })
    except: continue

all_news.sort(key=lambda x: x['raw'], reverse=True)

# 5. RENDER
st.title("🛡️ Multi-Asset Real-Time Scanner")
st.write(f"**Live IST:** {datetime.now(IST).strftime('%I:%M:%S %p')}")

if not all_news:
    st.error("Connection failed. Check your internet or Streamlit Cloud logs.")
else:
    for item in all_news:
        alert = "2px solid #ff4b4b" if "BEARISH" in item['impact'] else "1px solid #30363d"
        st.markdown(f"""
            <div class="news-card" style="border: {alert};">
                <div class="meta">
                    <span class="cat-tag">{item['cat']}</span>
                    <span class="impact-tag">{item['impact']}</span>
                </div>
                <div class="headline">{item['title']}</div>
                <div class="meta" style="margin-top:12px;">
                    <span style="color:#8b949e;">🕒 {item['time']}</span>
                    <a href="{item['link']}" target="_blank" style="color:#58a6ff; text-decoration:none;">Read Full Impact →</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
