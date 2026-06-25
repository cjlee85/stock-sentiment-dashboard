"""
Streamlit dashboard - Stock Sentiment vs Price Tracker

Install first:
    pip install streamlit pandas

Run:
    streamlit run app.py

Requires price_data.csv and news_sentiment.csv to already exist
(run 01_get_price_data.py and 02_get_news_sentiment.py first).
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Stock Sentiment Tracker", layout="wide")

st.title("📊 Stock Sentiment vs Price Dashboard")
st.caption("Tracking the relationship between financial news sentiment and stock price movement.")

# ---- Load data ----
try:
    price_df = pd.read_csv("price_data.csv")
    price_df["date"] = pd.to_datetime(price_df["date"])
except FileNotFoundError:
    st.error("price_data.csv not found. Run 01_get_price_data.py first.")
    st.stop()

try:
    news_df = pd.read_csv("news_sentiment.csv")
    news_df["date"] = pd.to_datetime(news_df["publishedAt"]).dt.date
    news_df["date"] = pd.to_datetime(news_df["date"])
except FileNotFoundError:
    st.error("news_sentiment.csv not found. Run 02_get_news_sentiment.py first.")
    st.stop()

# ---- Ticker selector ----
tickers = sorted(price_df["ticker"].unique())
selected = st.selectbox("Select a ticker", tickers)

price_filtered = price_df[price_df["ticker"] == selected]
news_filtered = news_df[news_df["ticker"] == selected]

daily_sentiment = (
    news_filtered.groupby("date")["sentiment"]
    .mean()
    .reset_index()
)

merged = pd.merge(price_filtered, daily_sentiment, on="date", how="inner")

# ---- KPI row ----
col1, col2, col3 = st.columns(3)

avg_sentiment = news_filtered["sentiment"].mean() if not news_filtered.empty else None
col1.metric("Avg Sentiment (7 days)", f"{avg_sentiment:.3f}" if avg_sentiment is not None else "N/A")

if len(merged) >= 3:
    corr = merged["Close"].corr(merged["sentiment"])
    col2.metric("Price/Sentiment Correlation", f"{corr:.3f}")
else:
    col2.metric("Price/Sentiment Correlation", "Not enough data yet")

col3.metric("Matched Days So Far", len(merged))

st.divider()

# ---- Main chart ----
st.subheader(f"{selected}: Price vs Sentiment Over Time")

if len(merged) >= 2:
    chart_data = merged.set_index("date")[["Close", "sentiment"]]
    st.line_chart(chart_data)
else:
    st.info(
        "Not enough overlapping days yet to plot a trend. "
        "Keep running the news script daily to build up history."
    )

st.divider()

# ---- Recent headlines table ----
st.subheader("Recent Headlines")
recent = news_filtered.sort_values("publishedAt", ascending=False)[
    ["publishedAt", "title", "sentiment"]
].head(10)
st.dataframe(recent, use_container_width=True)

st.divider()

# ---- Honest findings section ----
st.subheader("Findings")
st.markdown(
    f"""
- This dashboard currently has **{len(merged)} day(s)** of overlapping price and sentiment data for {selected}.
- A correlation number only becomes meaningful with roughly 10+ days of data — treat anything shown above as a work in progress, not a conclusion.
- Sentiment is scored using VADER, a general-purpose sentiment tool. It does not understand financial context directly (e.g. "misses estimates but raises guidance" may score oddly), which is a known limitation of this approach.
"""
)

st.caption("Data sources: NewsAPI, Yahoo Finance · Built with Python, pandas, VADER, Streamlit")
