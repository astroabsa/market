import streamlit as st
import feedparser
import requests
import io
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ... [Keep your Sentiment & UI Setup same] ...

# 4. UPDATED DATA FETCHING (Bypasses Blocks)
def fetch_secure_feed(url, cat_name):
    # This header tells the server "I am a real Chrome browser on Windows"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Use BytesIO to turn the web response into a format feedparser likes
        f = feedparser.parse(io.BytesIO(response.content))
        
        items = []
        for e in f.entries[:8]:
            dt = datetime(*e.published_parsed[:6], tzinfo=pytz.utc).astimezone(IST) if 'published_parsed' in e else datetime.now(IST)
            items.append({
                "cat": cat_name, "title": e.title, "link": e.link, 
                "time": dt.strftime("%I:%M %p"), "raw": dt, "impact": get_sentiment(e.title)
            })
        return items
    except Exception as e:
        # If it fails, we show nothing for that category instead of crashing
        return []

# 6. UPDATED PROCESSING LOOP
FEEDS = {
    "💎 BULLION/MCX": "https://www.kitco.com/rss/index.xml",
    "📊 NSE EQUITIES": "https://www.moneycontrol.com/rss/marketnews.xml",
    "📈 GLOBAL MACRO": "https://www.investing.com/rss/news_1.rss",
    "🏗️ BASE METALS": "https://www.investing.com/rss/news_476.rss",
    "₿ CRYPTO/TECH": "https://cointelegraph.com/rss"
}

all_news = []
for cat, url in FEEDS.items():
    all_news.extend(fetch_secure_feed(url, cat))

all_news.sort(key=lambda x: x['raw'], reverse=True)

# ... [Keep your Render/Watchlist logic same] ...
