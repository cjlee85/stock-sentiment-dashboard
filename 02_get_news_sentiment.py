"""
Step 2: Pull news headlines for MULTIPLE tickers and score sentiment.
Appends to a growing historical dataset instead of overwriting.

Run this on YOUR machine, once a day, manually for now (automation comes later).

Install first:
    pip install requests vaderSentiment pandas

Run:
    python 02_get_news_sentiment.py
"""

import os
import requests
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta

# ---- CONFIG ----
API_KEY = os.getenv("NEWS_API_KEY") # prevent from exposing API key

if not API_KEY:
    raise ValueError("NEWS_API_KEY is missing. Set it in your environment or Streamlit secrets.")
    
DAYS_BACK = 7
FILE_PATH = "news_sentiment.csv"   # one shared file for all tickers now

TICKERS = {
    "NVDA": "Nvidia",
    "AMD": "AMD",
    "INTC": "Intel",
    "TSLA": "Tesla",
}
# -----------------


def get_news(query, days_back, api_key):
    """Pull recent news headlines mentioning the company."""
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": api_key,
        "pageSize": 100,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "ok":
        print(f"Error from NewsAPI for '{query}':", data)
        return pd.DataFrame()

    articles = data.get("articles", [])
    print(f"Pulled {len(articles)} articles mentioning '{query}'")

    rows = []
    for a in articles:
        rows.append({
            "publishedAt": a["publishedAt"],
            "title": a["title"],
            "description": a["description"],
            "source": a["source"]["name"],
            "url": a["url"],   # critical for deduplication
        })

    return pd.DataFrame(rows)


def score_sentiment(df):
    """Add a sentiment score column using VADER."""
    analyzer = SentimentIntensityAnalyzer()
    df["sentiment"] = df["title"].apply(
        lambda text: analyzer.polarity_scores(text)["compound"] if text else 0
    )
    return df


def save_with_dedup(new_df, file_path):
    """Append new rows to the historical file, skipping anything already saved."""
    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
        existing_urls = set(existing_df["url"])

        # Only keep articles we haven't seen before
        new_only = new_df[~new_df["url"].isin(existing_urls)]

        combined = pd.concat([existing_df, new_only], ignore_index=True)
        added = len(new_only)
    else:
        combined = new_df
        added = len(new_df)

    combined.to_csv(file_path, index=False)
    print(f"\nAdded {added} new rows. Total dataset size: {len(combined)} rows.")
    return combined


if __name__ == "__main__":
    all_news = []

    for ticker, company in TICKERS.items():
        print(f"\n--- Fetching news for {ticker} ({company}) ---")
        df = get_news(company, DAYS_BACK, API_KEY)

        if not df.empty:
            df = score_sentiment(df)
            df["ticker"] = ticker
            all_news.append(df)

    if all_news:
        news_df = pd.concat(all_news, ignore_index=True)

        print("\nSample headlines with sentiment scores:")
        print(news_df[["ticker", "title", "sentiment"]].head(10))

        combined = save_with_dedup(news_df, FILE_PATH)

        print("\nPer-ticker average sentiment (today's pull only):")
        print(news_df.groupby("ticker")["sentiment"].mean())
    else:
        print("No news data retrieved for any ticker.")
