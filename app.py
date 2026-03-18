import streamlit as st
import feedparser
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. SETTINGS & REFRESH
st.set_page_config(page_title="Global Multi-Asset Scanner", layout="centered")
st_autorefresh(interval=60000, key="news_refresh")
IST = pytz.timezone('Asia/Kolkata')
analyzer = SentimentIntensityAnalyzer()

# 2. DIVERSIFIED SOURCE ENGINE
FEEDS = {
    "💎 BULLION/MCX": "https://www.kitco.com/rss/index.xml",
    "📊 NSE EQUITIES": "https://www.moneycontrol.com/rss/marketnews.xml",
    "📈 GLOBAL MACRO": "http://feeds.reuters.com/reuters/businessNews",
    "🏗️ BASE METALS": "https://www.investing.com/rss/news_476.rss",
    "₿ CRYPTO/TECH": "https://cointelegraph.com/rss"
}

# 3. MULTI-ASSET IMPACT ENGINE
def get_asset_impact(title):
    t = title.upper()
    score = analyzer.polarity_scores(title)['compound']
    
    # Bearish Triggers (Asset Specific)
    if any(w in t for w in ["RATE HIKE", "INFLATION SPIKE", "FII SELL", "DEFAULT"]): return "BEARISH 🔴"
    # Bullish Triggers (Asset Specific)
    if any(w in t for w in ["RATE CUT", "STIMULUS", "FII BUY", "FDI", "RECORD HIGH"]): return "BULLISH 🟢"
    
    if score >= 0.05: return "POSITIVE ⬆️"
    elif score <= -0.05: return "NEGATIVE ⬇️"
    return "NEUTRAL ⚪"

# 4. UI STYLING
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .news-card { padding: 15px; border-radius: 8px; background-color: #161b22; border: 1px solid #30363d; margin-bottom: 12px; }
    .headline { color: #f0f6fc !important; font-weight: 600; font-size: 1.05rem; margin-bottom: 8px; }
    .meta-row { display: flex; justify-content: space-between; font-size: 0.75rem; }
    .category { color: #58a6ff; font-weight: bold; border: 1px solid #58a6ff; padding: 1px 5px; border-radius: 3px; }
    .impact { color: #ffffff; background: #238636; padding: 2px 8px; border-radius: 4px; }
    .bearish { background: #da3633; }
    </style>
""", unsafe_allow_html=True)

# 5. KEYWORD ALERTS (User Input)
st.sidebar.title("🎯 Focus Watchlist")
watchlist = st.sidebar.text_input("Enter keywords (e.g. Reliance, Gold, HDFC)", "Nifty, Crude").upper().split(',')
watchlist = [w.strip() for w in watchlist]

# 6. DATA PROCESSING
all_news = []
for cat, url in FEEDS.items():
    try:
        f = feedparser.parse(url)
        for e in f.entries[:10]:
            dt = datetime(*e.published_parsed[:6], tzinfo=pytz.utc).astimezone(IST) if 'published_parsed' in e else datetime.now(IST)
            impact = get_asset_impact(e.title)
            all_news.append({
                "cat": cat, "title": e.title, "link": e.link, 
                "time": dt.strftime("%I:%M %p"), "raw": dt, "impact": impact
            })
    except: continue

all_news.sort(key=lambda x: x['raw'], reverse=True)

# 7. RENDER
st.title("📡 Multi-Asset Real-Time Scanner")
st.write(f"**Live IST:** {datetime.now(IST).strftime('%I:%M:%S %p')}")

for item in all_news:
    # Logic for Watchlist Highlighting
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
                <a href="{item['link']}" target="_blank" style="color:#58a6ff; text-decoration:none;">Full Report →</a>
            </div>
        </div>
    """, unsafe_allow_html=True)
