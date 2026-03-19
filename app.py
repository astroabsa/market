import streamlit as st
import requests
import time

NEWS_API_KEY = "cf8efaee440848faa4a6b34964cd0874"

def fetch_news():
    url = f"https://newsapi.org/v2/everything?q=india OR crude OR crypto&apiKey={NEWS_API_KEY}"
    return requests.get(url).json()["articles"]

def classify_news(title):
    t = title.lower()

    if "rbi" in t and "hike" in t:
        return "Bearish", "NSE", "Banking"
    elif "crude" in t:
        return "Bullish", "MCX", "Energy"
    elif "bitcoin" in t:
        return "Bullish", "CRYPTO", "Crypto"
    else:
        return "Neutral", "GENERAL", "General"

def impact_score(text):
    score = 1
    if any(w in text for w in ["war", "ban", "crisis"]):
        score += 3
    elif any(w in text for w in ["rise", "fall"]):
        score += 1
    return min(score, 5)

def option_chain_mock():
    # Replace with real API later
    return "Bullish", 1.3

def trade_engine(news_bias, option_bias, impact):
    score = impact

    if news_bias == option_bias:
        score += 2

    if score >= 4:
        return "🔥 STRONG TRADE"
    elif score >= 2:
        return "⚡ MODERATE"
    else:
        return "❌ AVOID"

st.title("🚀 PRO Market Scanner")

placeholder = st.empty()

while True:
    news = fetch_news()

    with placeholder.container():
        for n in news[:10]:
            title = n["title"]

            news_bias, market, sector = classify_news(title)
            impact = impact_score(title.lower())

            option_bias, pcr = option_chain_mock()

            decision = trade_engine(news_bias, option_bias, impact)

            st.markdown(f"""
            **{title}**
            
            Market: `{market}` | Sector: `{sector}`  
            Bias: `{news_bias}` | Impact: `{'🔥'*impact}`  
            Option Bias: `{option_bias}` (PCR: {pcr})  
            
            👉 **Decision: {decision}**
            ---
            """)

    time.sleep(20)
