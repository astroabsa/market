import streamlit as st
import requests
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------- CONFIG ---------------- #
NEWS_API_KEY = "cf8efaee440848faa4a6b34964cd0874"

REFRESH_TIME = 30  # seconds

analyzer = SentimentIntensityAnalyzer()

# ---------------- KEYWORDS ---------------- #
KEYWORDS = [
    "rbi", "inflation", "interest rate", "crude", "gold",
    "bitcoin", "crypto", "war", "fed", "recession",
    "opec", "ban", "approval", "policy"
]

# ---------------- FETCH NEWS ---------------- #
def fetch_news():
    url = f"https://newsapi.org/v2/everything?q=india OR crude OR crypto&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url).json()
        return res.get("articles", [])
    except:
        return []

# ---------------- FILTER ---------------- #
def filter_news(articles):
    filtered = []
    for art in articles:
        title = art["title"].lower()
        if any(k in title for k in KEYWORDS):
            filtered.append(art)
    return filtered

# ---------------- CLASSIFICATION ---------------- #
def classify_news(title):
    t = title.lower()

    if "rbi" in t and ("hike" in t or "increase" in t):
        return "Bearish", "NSE", "Banking"
    elif "rbi" in t and ("cut" in t or "decrease" in t):
        return "Bullish", "NSE", "Banking"
    elif "crude" in t or "opec" in t:
        return "Bullish", "MCX", "Energy"
    elif "gold" in t:
        return "Bullish", "MCX", "Metals"
    elif "war" in t:
        return "Bullish", "MCX", "Safe Haven"
    elif "bitcoin" in t or "crypto" in t:
        if "ban" in t:
            return "Bearish", "CRYPTO", "Crypto"
        return "Bullish", "CRYPTO", "Crypto"

    return "Neutral", "GENERAL", "General"

# ---------------- IMPACT ---------------- #
def impact_score(text):
    score = 1

    strong = ["war", "ban", "crisis", "approval", "etf"]
    medium = ["rise", "fall", "increase", "decrease"]

    for w in strong:
        if w in text:
            score += 3

    for w in medium:
        if w in text:
            score += 1

    return min(score, 5)

# ---------------- OPTION BIAS (MOCK) ---------------- #
def option_chain_mock():
    # Replace later with Upstox API
    return "Bullish", 1.3

# ---------------- CONFIDENCE ENGINE ---------------- #
def calculate_confidence(news_bias, option_bias, impact):
    score = impact

    if news_bias == option_bias:
        score += 3
    else:
        score -= 1

    return max(min(score, 10), 1)

# ---------------- TRADE DECISION ---------------- #
def get_trade_action(news_bias, confidence):
    if news_bias == "Neutral":
        return "SKIP"

    if confidence >= 7:
        return "BUY CALL" if news_bias == "Bullish" else "BUY PUT"
    elif confidence >= 4:
        return "WATCH"
    else:
        return "SKIP"

# ---------------- UI CARD ---------------- #
def display_card(title, market, sector, bias, impact, option_bias, action, confidence):

    if action == "BUY CALL":
        color = "green"
    elif action == "BUY PUT":
        color = "red"
    else:
        color = "gray"

    st.markdown(f"""
    ### 📰 {title}

    **🧭 Market:** {market} ({sector})  
    **📈 Bias:** {bias} {'🔥'*impact}  
    **📊 Option Bias:** {option_bias}  

    ### 👉 ACTION: {action}
    🎯 Confidence: {confidence}/10

    ---
    """)

# ---------------- STREAMLIT ---------------- #
st.set_page_config(layout="wide")
st.title("🚀 PRO Market Scanner (Action Based)")

placeholder = st.empty()

while True:
    articles = fetch_news()
    filtered = filter_news(articles)

    with placeholder.container():

        actionable_found = False

        for art in filtered[:15]:
            title = art["title"]

            news_bias, market, sector = classify_news(title)
            impact = impact_score(title.lower())

            option_bias, pcr = option_chain_mock()

            confidence = calculate_confidence(news_bias, option_bias, impact)
            action = get_trade_action(news_bias, confidence)

            # Show only useful trades
            if action != "SKIP":
                actionable_found = True
                display_card(title, market, sector, news_bias, impact, option_bias, action, confidence)

        if not actionable_found:
            st.info("No high-quality trade setups right now... wait for better signals ⏳")

    time.sleep(REFRESH_TIME)
