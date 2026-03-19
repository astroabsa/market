import streamlit as st
import requests
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

NEWS_API_KEY = "cf8efaee440848faa4a6b34964cd0874"

KEYWORDS = [
    "rbi", "inflation", "interest rate", "crude", "gold",
    "bitcoin", "crypto", "war", "fed", "recession", "policy"
]

def fetch_news():
    url = f"https://newsapi.org/v2/everything?q=india OR crypto OR crude&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    return response.json().get("articles", [])

def filter_news(articles):
    filtered = []
    for art in articles:
        title = art["title"].lower()
        if any(k in title for k in KEYWORDS):
            filtered.append(art)
    return filtered

def classify_market(news):
    text = news.lower()

    if "rbi" in text or "interest rate" in text:
        return "NSE"
    elif "crude" in text or "gold" in text:
        return "MCX"
    elif "bitcoin" in text or "crypto" in text:
        return "CRYPTO"
    else:
        return "GENERAL"

def sentiment_label(text):
    score = analyzer.polarity_scores(text)["compound"]
    if score > 0.2:
        return "Bullish"
    elif score < -0.2:
        return "Bearish"
    else:
        return "Neutral"

st.title("📡 Live Market News Scanner")

placeholder = st.empty()

while True:
    articles = fetch_news()
    filtered = filter_news(articles)

    output = []

    for art in filtered[:10]:
        title = art["title"]
        sentiment = sentiment_label(title)
        market = classify_market(title)

        label = f"{sentiment} : {market}"

        output.append({
            "Title": title,
            "Label": label,
            "Source": art["source"]["name"]
        })

    with placeholder.container():
        for item in output:
            st.markdown(f"""
            **{item['Title']}**  
            Label: `{item['Label']}`  
            Source: {item['Source']}
            ---
            """)

    time.sleep(30)
