import streamlit as st
import feedparser
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. SETTINGS
st.set_page_config(page_title="Multi-Asset Scanner 2026", layout="centered")
st_autorefresh(interval=180000, key="news_refresh")
IST = pytz.timezone('Asia/Kolkata')
analyzer = SentimentIntensityAnalyzer()

# 2. UPDATED 2026 VERIFIED FEEDS
# Replaced Moneycontrol/Reuters with more stable 2026 Investing.com & NSE endpoints
FEEDS = {
    "🇮🇳 NSE/BSE INDIA": "https://in.investing.com/rss/news_301.rss",
    "📊 NSE CORPORATE": "https://www.nseindia.com/static/rss/corporate_announcements.xml",
    "🔥 MCX/ENERGY": "https://in.investing.com/rss/news_11.rss",
    "💎 BULLION/GOLD": "https://www.kitco.com/rss/index.xml",
    "🌍 GLOBAL MACRO": "https://in.investing.com/rss/news_1.rss",
    "₿ CRYPTO/TECH": "https://cointelegraph.com/rss"
}

def get_asset_impact(title):
    t = title.upper()
    score = analyzer.polarity_scores(title)['compound']
    # 2026 High-Impact Keywords
    if any(w in t for w in ["WAR", "IRAN", "STRIKE", "FII SELL", "CRUDE SPIKE"]): return "BEARISH 🔴"
    if any(w in t for w in ["RALLY", "FII BUY", "STIMULUS", "GDP BEAT"]): return "BULLISH 🟢"
    if score >= 0.05: return "POSITIVE ⬆️"
    elif score <= -0.05: return "NEGATIVE ⬇️"
    return "NEUTRAL ⚪"

# 3. UI STYLING (Forced Contrast)
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .news-card { padding: 15px; border-radius: 8px; background-color: #161b22; border: 1px solid #30363d; margin-bottom: 12px; }
    .headline { color: #ffffff !important; font-weight: 600; font-size: 1.05rem; margin-bottom: 8px; text-decoration: none; }
    .meta-row { display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 5px; }
    .category { color: #58a6ff; font-weight: bold; border: 1px solid #58a6ff; padding: 1px 5px; border-radius: 3px; }
    .impact { color: #ffffff; background: #238636; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .bearish { background: #da3633; }
    </style>
""", unsafe_allow_html=True)

# 4. WATCHLIST
st.sidebar.title("🎯 Focus Watchlist")
watchlist_input = st.sidebar.text_input("Keywords (e.g. Reliance, Gold, HDFC)", "Nifty, Crude")
watchlist = [w.strip().upper() for w in watchlist_input.split(',')]

# 5. DATA PROCESSING
all_news = []
for cat, url in FEEDS.items():
    try:
        # User-Agent header is sometimes needed for Indian feeds to avoid 403 blocks
        f = feedparser.parse(url)
        if not f.entries:
            continue # Skip if feed is empty
            
        for e in f.entries[:10]:
            dt = datetime(*e.published_parsed[:6], tzinfo=pytz.utc).astimezone(IST) if hasattr(e, 'published_parsed') else datetime.now(IST)
            impact = get_asset_impact(e.title)
            all_news.append({
                "cat": cat, "title": e.title, "link": e.link, 
                "time": dt.strftime("%I:%M %p"), "raw": dt, "impact": impact
            })
    except Exception as ex:
        continue

all_news.sort(key=lambda x: x['raw'], reverse=True)

# 6. RENDER
st.title("📡 Live Multi-Asset Scanner")
st.write(f"**Current IST:** {datetime.now(IST).strftime('%I:%M:%S %p')}")

if not all_news:
    st.error("No active news found. The Indian feeds might be temporarily blocking the connection. Try refreshing in 1 minute.")
else:
    for item in all_news:
        is_watched = any(word in item['title'].upper() for word in watchlist)
        border_style = "2px solid #f2cc60" if is_watched else "1px solid #30363d"
        impact_class = "bearish" if "BEARISH" in item['impact'] or "NEGATIVE" in item['impact'] else ""

        st.markdown(f"""
            <div class="news-card" style="border: {border_style};">
                <div class="meta-row">
                    <span class="category">{item['cat']}</span>
                    <span class="impact {impact_class}">{item['impact']}</span>
                </div>
                <div class="headline">{"⭐ " if is_watched else ""}{item['title']}</div>
                <div class="meta-row" style="margin-top:10px;">
                    <span style="color:#8b949e;">🕒 {item['time']}</span>
                    <a href="{item['link']}" target="_blank" style="color:#58a6ff; text-decoration:none;">Details →</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
