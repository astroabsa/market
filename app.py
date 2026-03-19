import streamlit as st
import requests
import time
import pandas as pd

# ---------------- CONFIG ---------------- #
NEWS_API_KEY = "cf8efaee440848faa4a6b34964cd0874"
REFRESH_TIME = 30

# ---------------- FETCH NEWS ---------------- #
def fetch_news():
    try:
        url = f"https://newsapi.org/v2/everything?q=crypto OR crude OR rbi OR gold OR nifty&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        res = requests.get(url, timeout=5)
        return res.json().get("articles", [])
    except:
        return []

# ---------------- CLASSIFICATION ---------------- #
def classify_news(title):
    t = title.lower()

    if "bitcoin" in t or "crypto" in t:
        if any(x in t for x in ["fall", "drop", "crash"]):
            return "Bearish", "CRYPTO"
        elif any(x in t for x in ["etf", "approval", "surge"]):
            return "Bullish", "CRYPTO"
        return "Neutral", "CRYPTO"

    if "rbi" in t:
        if "hike" in t:
            return "Bearish", "NSE"
        elif "cut" in t:
            return "Bullish", "NSE"

    if "crude" in t:
        return "Bullish", "MCX"

    if "gold" in t:
        return "Bullish", "MCX"

    return "Neutral", "GENERAL"

# ---------------- IMPACT ---------------- #
def impact_score(text):
    score = 1
    if any(w in text for w in ["war", "ban", "crisis"]):
        score += 3
    if any(w in text for w in ["rise", "fall"]):
        score += 1
    return min(score, 5)

# ---------------- FETCH MARKET DATA ---------------- #
def fetch_yahoo(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=5m"
        data = requests.get(url, timeout=5).json()

        closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        df = pd.DataFrame(closes, columns=["close"])
        df.dropna(inplace=True)

        return df
    except:
        return None

def fetch_binance():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=50"
        data = requests.get(url, timeout=5).json()

        df = pd.DataFrame(data, columns=["t","o","h","l","c","v","ct","q","n","tb","tq","i"])
        df["close"] = pd.to_numeric(df["c"], errors="coerce")
        df.dropna(inplace=True)

        return df[["close"]]
    except:
        return None

# ---------------- TREND ---------------- #
def trend(df):
    if df is None or df.empty or len(df) < 20:
        return "Unknown"

    df["ema20"] = df["close"].ewm(span=20).mean()

    price = df["close"].iloc[-1]
    ema = df["ema20"].iloc[-1]

    if price > ema:
        return "Bullish"
    elif price < ema:
        return "Bearish"
    return "Neutral"

# ---------------- CONFIDENCE ---------------- #
def confidence(news, trend_val, impact):
    score = impact

    if trend_val == "Unknown":
        return 1

    if news == trend_val:
        score += 3
    else:
        score -= 2

    return max(min(score, 10), 1)

# ---------------- ACTION ---------------- #
def action(news, trend_val, conf):

    if trend_val == "Unknown":
        return "NO DATA"

    if news == "Neutral":
        return "SKIP"

    if news != trend_val:
        return "⚠️ TRAP"

    if conf >= 7:
        return "BUY CALL" if news == "Bullish" else "BUY PUT"

    elif conf >= 4:
        return "WATCH"

    return "SKIP"

# ---------------- STREAMLIT ---------------- #
st.set_page_config(layout="wide")
st.title("🚀 Ultimate Market Scanner")

placeholder = st.empty()

while True:

    news_data = fetch_news()

    # Fetch trends
    nifty_df = fetch_yahoo("^NSEI")
    bank_df = fetch_yahoo("^NSEBANK")
    gold_df = fetch_yahoo("GLD")
    crude_df = fetch_yahoo("USO")
    btc_df = fetch_binance()

    trends = {
        "NSE": trend(nifty_df),
        "BANK": trend(bank_df),
        "MCX_GOLD": trend(gold_df),
        "MCX_CRUDE": trend(crude_df),
        "CRYPTO": trend(btc_df)
    }

    with placeholder.container():

        st.subheader("📊 Market Trends")
        st.write(trends)

        found = False

        for n in news_data[:20]:

            title = n["title"]
            news_bias, market = classify_news(title)
            imp = impact_score(title.lower())

            if market == "NSE":
                t = trends["NSE"]
            elif market == "MCX":
                t = trends["MCX_CRUDE"]
            elif market == "CRYPTO":
                t = trends["CRYPTO"]
            else:
                t = "Unknown"

            conf = confidence(news_bias, t, imp)
            act = action(news_bias, t, conf)

            if act not in ["SKIP", "NO DATA"]:

                found = True

                st.markdown(f"""
                ### 📰 {title}

                Market: {market}  
                News Bias: {news_bias} {'🔥'*imp}  
                Trend: {t}  

                👉 ACTION: {act}  
                🎯 Confidence: {conf}/10
                ---
                """)

        if not found:
            st.info("No strong aligned trades right now ⏳")

    time.sleep(REFRESH_TIME)
