import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

symbol = "AAPL"
interval = "1m"
now = datetime.utcnow()
start = now - timedelta(days=7)

print(f"Fetching {symbol} from {start} to {now} with interval {interval}")
df = yf.download(symbol, start=start, end=now, interval=interval, progress=False, threads=False)

print(df.head())
print(f"Retrieved {len(df)} rows")
