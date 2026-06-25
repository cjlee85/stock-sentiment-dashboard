# 📊 Stock Sentiment vs Price Tracker

**Live dashboard:** https://stock-sentiment-dashboard-jgtkfgvyjgvjuejsjdzpzs.streamlit.app/
*(may take ~30-60 seconds to wake up on first visit — Streamlit Cloud free tier)*

A small data pipeline and dashboard that tracks financial news sentiment alongside stock price movement for a handful of AI-adjacent companies (NVDA, AMD, INTC, TSLA).

## What it does

```
NewsAPI ──┐
          ├──► sentiment scoring (VADER) ──┐
Yahoo     │                                ├──► merge by date ──► Streamlit dashboard
Finance ──┘──► price history ──────────────┘
```

- Pulls daily stock price history from Yahoo Finance
- Pulls recent news headlines per ticker from NewsAPI
- Scores each headline's sentiment using VADER (-1 to +1)
- Appends new data daily while de-duplicating by article URL, building a real historical dataset over time rather than a one-off snapshot
- Merges price and sentiment by date and visualizes both in an interactive dashboard

## Why I built it

I wanted to learn the practical side of a data pipeline — collection, storage, cleaning, and visualization — using a domain I already understand (markets) while applying machine learning concepts I was learning at the same time. I chose AI-adjacent companies specifically because of my interest in the AI industry.

## Tech stack

- Python (pandas, requests)
- VADER (NLP sentiment scoring)
- yfinance (price data)
- NewsAPI (news data)
- Streamlit (dashboard)

## Known limitations

- VADER is a general-purpose sentiment tool, not finance-specific — it can misread financial language (e.g. "misses estimates but raises guidance" reads ambiguously to it)
- NewsAPI's free tier only returns a limited recent window of articles, so the historical dataset builds up gradually rather than being available all at once
- Correlation figures are only meaningful once enough days of overlapping data have accumulated — early results should be read as pipeline validation, not financial conclusions

## What I'd do next

- Let the dataset grow for a few weeks and revisit the correlation numbers with a real sample size
- Test whether sentiment has any next-day predictive signal, once there's enough data to do that responsibly
- Automate the daily pull with GitHub Actions instead of running scripts manually

## Running it locally

```bash
pip install yfinance pandas requests vaderSentiment streamlit

python 01_get_price_data.py
python 02_get_news_sentiment.py
streamlit run app.py
```
