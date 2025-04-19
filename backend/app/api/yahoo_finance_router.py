from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pathlib import Path
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import traceback
import sys

router = APIRouter()

CACHE_DIR = Path(__file__).parent.parent / "data" / "yfinance_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

INTERVAL_WINDOWS = {
    "1m": timedelta(days=7),
    "5m": timedelta(days=30),
    "15m": timedelta(days=60),
    "30m": timedelta(days=60),
    "1h": timedelta(days=730),
    "1d": timedelta(days=3650),
    "1wk": timedelta(days=3650),
    "1mo": timedelta(days=3650)
}

@router.get("/history/{symbol}")
def get_historical_data(
    symbol: str,
    interval: str = Query("1d", enum=list(INTERVAL_WINDOWS.keys())),
    start: Optional[str] = Query("auto"),
    end: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    cache_file = CACHE_DIR / f"{symbol}_{interval}.csv"
    now = datetime.utcnow()

    max_back = INTERVAL_WINDOWS[interval]
    min_allowed_start = now - max_back

    if start == "auto":
        start_date = min_allowed_start
    else:
        start_date = pd.to_datetime(start)

    end_date = pd.to_datetime(end or now)

    # Normalize timezone for safety
    if start_date.tzinfo:
        start_date = start_date.tz_localize(None)
    if end_date.tzinfo:
        end_date = end_date.tz_localize(None)

    if start_date < min_allowed_start:
        start_date = min_allowed_start

    print(f"[DEBUG] Fetching {symbol} from {start_date} to {end_date} with interval {interval}")

    if cache_file.exists():
        try:
            df_cache = pd.read_csv(cache_file, index_col=0)
            df_cache.index = pd.to_datetime(df_cache.index, errors='coerce')
            df_cache = df_cache[~df_cache.index.isna()]
            print(f"[DEBUG] Loaded cache with {len(df_cache)} valid datetime rows")
        except Exception as e:
            print(f"[ERROR] Failed to load cache: {e}")
            df_cache = None
            cache_file.unlink(missing_ok=True)
    else:
        df_cache = None

    full_df = df_cache if df_cache is not None else pd.DataFrame()

    if df_cache is not None and not df_cache.empty:
        last_date = df_cache.index.max()
        print(f"[DEBUG] last_date value: {last_date} (type: {type(last_date)})")
        if pd.isna(last_date):
            fetch_from = start_date
        else:
            fetch_from = last_date + timedelta(minutes=1)
    else:
        fetch_from = start_date

    # Normalize fetch_from timezone
    if fetch_from.tzinfo:
        fetch_from = fetch_from.tz_localize(None)

    batched_data = []
    current_start = fetch_from
    window = INTERVAL_WINDOWS[interval]

    while current_start < end_date:
        current_end = min(current_start + window, end_date)
        print(f"[DEBUG] Downloading: {symbol} from {current_start} to {current_end}")
        try:
            df = yf.download(
                symbol,
                start=current_start,
                end=current_end,
                interval=interval,
                progress=False,
                threads=False
            )
            if isinstance(df, pd.DataFrame) and not df.empty:
                df.index = pd.to_datetime(df.index)
                batched_data.append(df)
                print(f"[DEBUG] Downloaded {len(df)} rows")
            else:
                print("[DEBUG] No data returned for this batch")
        except Exception as e:
            print(f"[ERROR] Failed batch: {e}")
        current_start = current_end + timedelta(minutes=1)

    if batched_data:
        df_new = pd.concat(batched_data)
        df_combined = pd.concat([full_df, df_new]) if not full_df.empty else df_new
        df_combined = df_combined[~df_combined.index.duplicated(keep="last")]
        df_combined.sort_index(inplace=True)
        df_combined.to_csv(cache_file)
        print(f"[DEBUG] Saved updated data to cache with {len(df_combined)} rows")
    elif full_df is not None and not full_df.empty:
        df_combined = full_df
        print("[DEBUG] Used existing cached data")
    else:
        raise HTTPException(status_code=404, detail="No data found for this symbol")

    try:
        df_combined = df_combined.sort_index(ascending=False)

        if hasattr(df_combined.index, 'tz') and df_combined.index.tz is not None:
            df_combined.index = df_combined.index.tz_localize(None)

        for col in df_combined.columns:
            if pd.api.types.is_datetime64tz_dtype(df_combined[col]):
                df_combined[col] = df_combined[col].dt.tz_localize(None)

        df_combined = df_combined.replace({np.nan: None, np.inf: None, -np.inf: None})
        df_combined.index = df_combined.index.astype(str)

        preview = df_combined.head(limit)
        print("[DEBUG] DataFrame preview constructed successfully.")
        return {"preview": preview.to_json()}
    except Exception as e:
        print("[CRITICAL] Exception caught while preparing response:")
        traceback.print_exc(file=sys.stdout)
        raise HTTPException(status_code=500, detail=f"Response error: {str(e)}")

@router.get("/info/{symbol}")
def get_symbol_info(symbol: str):
    try:
        ticker=yf.Ticker(symbol)
        info=ticker.info
        if not info:
            raise HTTPException(status_code=404, detail="No information found for this symbol.")
        return info
    except Exception as e:
        print((f"[ERROR] Failed to get info for {symbol}: {e}"))
        raise HTTPException(status_code=500, detail=str(e))

        