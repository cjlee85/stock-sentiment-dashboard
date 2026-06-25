"""
01_get_price_data.py

Pull price data for multiple tickers and save to a single CSV.

Install:
    pip install yfinance pandas

Run:
    python 01_get_price_data.py
"""

import yfinance as yf
import pandas as pd

TICKERS = ["NVDA", "AMD", "INTC", "TSLA"]
PERIOD = "6mo"
FILE_PATH = "price_data.csv"

all_data = []

for ticker in TICKERS:
    print(f"\nPulling {PERIOD} of price data for {ticker}...")

    try:
        data = yf.download(
            ticker,
            period=PERIOD,
            progress=False,
            auto_adjust=False
        )

        if data.empty:
            print(f"WARNING: No data returned for {ticker}")
            continue

        # Move index into columns
        data = data.reset_index()

        # Handle MultiIndex columns from newer yfinance versions
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [
                col[0] if isinstance(col, tuple) else col
                for col in data.columns
            ]

        print(f"{ticker} columns: {list(data.columns)}")

        # Find the date column
        date_col = None

        for col in data.columns:
            if str(col).lower() in ["date", "datetime"]:
                date_col = col
                break

        if date_col is None:
            raise ValueError(
                f"Could not find date column. Columns: {list(data.columns)}"
            )

        # Standardize date column name
        data = data.rename(columns={date_col: "date"})

        # Convert date safely
        data["date"] = pd.to_datetime(
            data["date"],
            errors="coerce"
        )

        # Remove bad rows
        data = data.dropna(subset=["date"])

        # Add ticker identifier
        data["ticker"] = ticker

        all_data.append(data)

        print(f"Loaded {len(data)} rows for {ticker}")

    except Exception as e:
        print(f"ERROR processing {ticker}:")
        print(e)

if not all_data:
    print("No price data was collected.")
else:
    combined = pd.concat(all_data, ignore_index=True)

    combined.to_csv(FILE_PATH, index=False)

    print(f"\nSaved combined dataset to {FILE_PATH}")
    print(f"Total rows: {len(combined)}")

    print("\nRows per ticker:")
    print(combined.groupby("ticker").size())