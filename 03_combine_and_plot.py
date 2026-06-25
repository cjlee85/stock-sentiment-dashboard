"""
Step 3: Combine price data and sentiment data, plot them together.
Run this on YOUR machine, in the same folder as your two CSV files.

Requires the CSVs already created by:
    01_get_price_data.py     -> NVDA_price_data.csv
    02_get_news_sentiment.py -> NVDA_news_sentiment.csv

Install first:
    pip install pandas matplotlib

Run:
    python 03_combine_and_plot.py
"""

import pandas as pd
import matplotlib.pyplot as plt

TICKER = "NVDA"

# ---- Load both datasets ----
price_df = pd.read_csv(f"{TICKER}_price_data.csv")
print("\nDEBUG - raw price CSV columns:", list(price_df.columns))
print("DEBUG - first few rows:\n", price_df.head())

news_df = pd.read_csv(f"{TICKER}_news_sentiment.csv")

# Convert news timestamps to just the date (drop time-of-day) so we can group by day
news_df["date"] = pd.to_datetime(news_df["publishedAt"]).dt.date

# Average sentiment per day (could be multiple headlines per day)
daily_sentiment = news_df.groupby("date")["sentiment"].mean().reset_index()
daily_sentiment["date"] = pd.to_datetime(daily_sentiment["date"])

print("Daily average sentiment:")
print(daily_sentiment)

# ---- Merge price and sentiment on matching dates ----
price_df_reset = price_df.copy()

print("\nDEBUG - price_df_reset columns:", list(price_df_reset.columns))

# Whatever the first column is called, treat it as the date column
first_col = price_df_reset.columns[0]
price_df_reset = price_df_reset.rename(columns={first_col: "date"})

# errors="coerce" turns anything unparseable into NaT instead of crashing
price_df_reset["date"] = pd.to_datetime(price_df_reset["date"], errors="coerce")

# Drop any rows where the date failed to parse (e.g. stray header/junk rows)
bad_rows = price_df_reset["date"].isna().sum()
if bad_rows > 0:
    print(f"DEBUG - dropping {bad_rows} rows with unparseable dates")
price_df_reset = price_df_reset.dropna(subset=["date"])

merged = pd.merge(price_df_reset, daily_sentiment, on="date", how="inner")

print(f"\nMatched {len(merged)} days where we have BOTH price and sentiment data")
print(merged[["date", "Close", "sentiment"]])

if len(merged) < 3:
    print("\nNote: very few overlapping days. This is expected with only "
          "7 days of free-tier news data. Run the news script for a few "
          "days in a row to build up more matched days over time.")

# ---- Plot both on the same chart (dual y-axis) ----
fig, ax1 = plt.subplots(figsize=(10, 5))

color1 = "tab:blue"
ax1.set_xlabel("Date")
ax1.set_ylabel("Close Price (USD)", color=color1)
ax1.plot(merged["date"], merged["Close"], color=color1, marker="o", label="Price")
ax1.tick_params(axis="y", labelcolor=color1)

ax2 = ax1.twinx()
color2 = "tab:red"
ax2.set_ylabel("Avg Daily Sentiment", color=color2)
ax2.plot(merged["date"], merged["sentiment"], color=color2, marker="s", label="Sentiment")
ax2.tick_params(axis="y", labelcolor=color2)
ax2.axhline(0, color="gray", linestyle="--", alpha=0.3)

plt.title(f"{TICKER}: Price vs News Sentiment")
fig.tight_layout()
plt.savefig(f"{TICKER}_price_vs_sentiment.png")
print(f"\nChart saved as {TICKER}_price_vs_sentiment.png")
plt.show()

# ---- Quick correlation check ----
if len(merged) >= 3:
    correlation = merged["Close"].corr(merged["sentiment"])
    print(f"\nCorrelation between price and sentiment: {correlation:.3f}")
    print("(Close to 0 = no relationship, close to +1 or -1 = strong relationship)")
    print("With this few data points, don't read too much into this number yet —")
    print("it's a starting signal, not a conclusion. More days of data will make it meaningful.")
