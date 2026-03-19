import streamlit as st
import requests
import time
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------- CONFIG ---------------- #
NEWS_API_KEY = "cf8efaee440848faa4a6b34964cd0874"
REFRESH_TIME = 30

analyzer = SentimentIntensityAnalyzer()

# ---------------- KEYWORDS ---------------- #
KEYWORDS = [
    "rbi", "inflation", "interest rate", "crude", "gold",
    "bitcoin", "crypto", "war", "fed", "recession",
    "opec", "ban", "approval", "policy"
]

# ---------------- FETCH NEWS ---------------- #
def fetch_news():
    url = f"https://newsapi.org/v2/everything?q=crypto OR bitcoin OR crude OR rbi&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url).json()
        return res.get("articles", [])
    except:
        return []

# ---------------- FILTER ---------------- #
def filter_news(articles):
    return [a for a in articles if any(k in a["title"].lower() for k in KEYWORDS)]

# ---------------- SMART CLASSIFICATION ---------------- #
def classify_news(title):
    t = title.lower()

    # Crypto logic
    if "bitcoin" in t or "crypto" in t:
        if any(x in t for x in ["falls", "drops", "pullback", "crash"]):
            return "Bearish", "CRYPTO", "Crypto"
        elif any(x in t for x in ["etf", "approval", "adoption", "surge"]):
            return "Bullish", "CRYPTO", "Crypto"
        elif "ban" in t or "crackdown" in t:
            return "Bearish", "CRYPTO", "Crypto"
        else:
            return "Neutral", "CRYPTO", "Crypto"

    # NSE logic
    if "rbi" in t:
        if "hike" in t:
            return "Bearish", "NSE", "Banking"
        elif "cut" in t:
            return "Bullish", "NSE", "Banking"

    # MCX logic
    if "crude" in t or "opec" in t:
        return "Bullish", "MCX", "Energy"

    if "gold" in t:
        return "Bullish", "MCX", "Metals"

    return "Neutral", "GENERAL", "General"

# ---------------- IMPACT ---------------- #
def impact_score(text):
    score = 1
    strong = ["war", "ban", "crisis", "etf", "approval"]
    medium = ["rise", "fall", "increase", "decrease"]

    for w in strong:
        if w in text:
            score += 3
    for w in medium:
        if w in text:
            score += 1

    return min(score, 5)

# ---------------- FETCH BTC PRICE ---------------- #
def fetch_btc_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=50"
    data = requests.get(url).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "ct","qav","trades","tb","tq","ignore"
    ])

    df["close"] = df["close"].astype(float)
    return df

# ---------------- TREND ---------------- #
def calculate_trend(df):
    df["ema20"] = df["close"].ewm(span=20).mean()
    price = df["close"].iloc[-1]
    ema = df["ema20"].iloc[-1]

    if price > ema:
        return "Bullish"
    elif price < ema:
        return "Bearish"
    return "Neutral"

# ---------------- OPTION MOCK ---------------- #
def option_bias_mock():
    return "Bullish"

# ---------------- CONFIDENCE ---------------- #
def calculate_confidence(news_bias, trend, impact):
    score = impact

    if news_bias == trend:
        score += 3
    elif news_bias != trend:
        score -= 2

    return max(min(score, 10), 1)

# ---------------- FINAL DECISION ---------------- #
def final_action(news_bias, trend, confidence):

    if news_bias == "Neutral":
        return "SKIP"

    if news_bias != trend:
        return "⚠️ TRAP (Conflict)"

    if confidence >= 7:
        return "BUY CALL" if news_bias == "Bullish" else "BUY PUT"
    elif confidence >= 4:
        return "WATCH"

    return "SKIP"

# ---------------- UI ---------------- #
def display_card(title, market, bias, impact, trend, action, confidence):

    st.markdown(f"""
    ### 📰 {title}

    **🧭 Market:** {market}  
    **📈 News Bias:** {bias} {'🔥'*impact}  
    **📉 Trend:** {trend}  

    ### 👉 ACTION: {action}
    🎯 Confidence: {confidence}/10

    ---
    """)

# ---------------- STREAMLIT ---------------- #
st.set_page_config(layout="wide")
st.title("🚀 PRO Market Scanner (News + Price Intelligence)")

placeholder = st.empty()

while True:
    articles = fetch_news()
    filtered = filter_news(articles)

    btc_df = fetch_btc_data()
    trend = calculate_trend(btc_df)

    with placeholder.container():

        found = False

        for art in filtered[:15]:
            title = art["title"]

            news_bias, market, sector = classify_news(title)
            impact = impact_score(title.lower())

            confidence = calculate_confidence(news_bias, trend, impact)
            action = final_action(news_bias, trend, confidence)

            if action not in ["SKIP"]:
                found = True
                display_card(title, market, news_bias, impact, trend, action, confidence)

        if not found:
            st.info("No strong setups right now — market not aligned with news ⏳")

    time.sleep(REFRESH_TIME)
