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


@router.get("/actions/{symbol}")
def get_actions(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        actions = ticker.actions
        if actions is None or actions.empty:
            raise HTTPException(status_code=404, detail="No corporate actions found for this symbol")
        actions.index = actions.index.astype(str)
        return {"actions": actions.to_dict(orient="index")}
    except Exception as e:
        print(f"[ERROR] Failed to fetch actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dividends/{symbol}")
def get_dividends(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        dividends = ticker.dividends
        if dividends is None or dividends.empty:
            raise HTTPException(status_code=404, detail="No dividends found for this symbol")
        dividends.index = dividends.index.astype(str)
        return {"dividends": dividends.to_dict()}
    except Exception as e:
        print(f"[ERROR] Failed to fetch dividends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/splits/{symbol}")
def get_splits(symbol: str):
    
    try:
        ticker = yf.Ticker(symbol)
        splits = ticker.splits
        if splits is None or splits.empty:
            raise HTTPException(status_code=404, detail="No splits found for this symbol")
        splits.index = splits.index.astype(str)
        return {"splits": splits.to_dict()}
    except Exception as e:
        print(f"[ERROR] Failed to fetch splits: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/financials/{symbol}")

def get_financials(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        financials = ticker.financials

        if financials is None or financials.empty:
            raise HTTPException(status_code=404, detail="No financial data found for this symbol")

        financials.index = financials.index.astype(str)
        financials.columns = financials.columns.astype(str)

        # ⛏️ Curățăm NaN, inf, -inf
        cleaned = financials.replace({np.nan: None, np.inf: None, -np.inf: None})

        return {"financials": cleaned.to_dict()}
    except Exception as e:
        print(f"[ERROR] Failed to fetch financials for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/balance-sheet/{symbol}")
def get_balance_sheet(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        balance_sheet = ticker.balance_sheet

        if balance_sheet is None or balance_sheet.empty:
            raise HTTPException(status_code=404, detail="No balance sheet data found for this symbol")

        balance_sheet.index = balance_sheet.index.astype(str)
        balance_sheet.columns = balance_sheet.columns.astype(str)

        cleaned = balance_sheet.replace({np.nan: None, np.inf: None, -np.inf: None})
        return {"balance_sheet": cleaned.to_dict()}
    except Exception as e:
        print(f"[ERROR] Failed to fetch balance sheet for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cashflow/{symbol}")
def get_cashflow(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        cashflow = ticker.cashflow

        if cashflow is None or cashflow.empty:
            raise HTTPException(status_code=404, detail="No cash flow data found for this symbol")

        cashflow.index = cashflow.index.astype(str)
        cashflow.columns = cashflow.columns.astype(str)

        cleaned = cashflow.replace({np.nan: None, np.inf: None, -np.inf: None})
        return {"cashflow": cleaned.to_dict()}
    except Exception as e:
        print(f"[ERROR] Failed to fetch cashflow for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sustainability/{symbol}")
def get_sustainability(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        sustainability = ticker.sustainability

        if sustainability is None or sustainability.empty:
            raise HTTPException(status_code=404, detail="No sustainability data found for this symbol")

        sustainability.index = sustainability.index.astype(str)
        cleaned = sustainability.replace({np.nan: None, np.inf: None, -np.inf: None})
        return {"sustainability": cleaned.to_dict()}
    except Exception as e:
        print(f"[ERROR] Failed to fetch sustainability data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{symbol}")
def get_recommendations(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        recommendations = ticker.recommendations

        if recommendations is None or recommendations.empty:
            raise HTTPException(status_code=404, detail="No recommendation data found for this symbol")

        recommendations.index = recommendations.index.astype(str)
        cleaned = recommendations.replace({np.nan: None, np.inf: None, -np.inf: None})
        return {"recommendations": cleaned.to_dict(orient="records")}
    except Exception as e:
        print(f"[ERROR] Failed to fetch recommendations for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar/{symbol}")
def get_calendar(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        calendar_raw = ticker.calendar

        if calendar_raw is None:
            raise HTTPException(status_code=404, detail="No calendar data found")

        # Convert DataFrame to dict or use dict as-is
        if isinstance(calendar_raw, pd.DataFrame):
            calendar_dict = calendar_raw.to_dict()
            # Flatten: take first value from Series
            calendar = {
                key: (value[0] if isinstance(value, (pd.Series, list)) else value)
                for key, value in calendar_dict.items()
            }
        elif isinstance(calendar_raw, dict):
            calendar = calendar_raw
        else:
            raise HTTPException(status_code=500, detail="Unexpected calendar format")

        # Normalize NaN
        cleaned = {
            k: (None if pd.isna(v) else v)
            for k, v in calendar.items()
        }

        return {"calendar": cleaned}

    except Exception as e:
        print(f"[ERROR] calendar fetch failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/options/{symbol}")
def get_options_expirations(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        expirations = ticker.options

        if not expirations:
            raise HTTPException(status_code=404, detail="No options expirations found")

        return {"expirations": expirations}
    except Exception as e:
        print(f"[ERROR] options expirations fetch failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/isin/{symbol}")
def get_isin(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        isin = ticker.isin

        if not isin:
            raise HTTPException(status_code=404, detail="ISIN not available")

        return {"symbol": symbol.upper(), "isin": isin}
    except Exception as e:
        print(f"[ERROR] Failed to fetch ISIN for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/news/{symbol}")
def get_news(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news

        if not news:
            raise HTTPException(status_code=404, detail="No news found")

        return {"symbol": symbol.upper(), "news": news}
    except Exception as e:
        print(f"[ERROR] Failed to fetch news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/major-holders/{symbol}")
def get_major_holders(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.major_holders

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No major holders found")

        # Convertim într-o listă de perechi (label, valoare)
        result = df.reset_index().values.tolist()
        return {"symbol": symbol.upper(), "major_holders": result}

    except Exception as e:
        print(f"[ERROR] Failed to fetch major holders for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/institutional-holders/{symbol}")
def get_institutional_holders(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.institutional_holders

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No institutional holders data found")

        df = df.replace({np.nan: None})
        df = df.reset_index(drop=True)

        return df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mutualfund-holders/{symbol}")
def get_mutualfund_holders(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.mutualfund_holders

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No mutual fund holders data found")

        df = df.replace({np.nan: None})
        df = df.reset_index(drop=True)

        return df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sectors")
def get_all_sectors():
    sectors_keys = [
        "basic-materials",
        "communication-services",
        "consumer-cyclical",
        "consumer-defensive",
        "energy",
        "financial-services",
        "healthcare",
        "industrials",
        "real-estate",
        "technology",
        "utilities"
        ]
    return {"sectors": sectors_keys}

@router.get("/sectors/{sector}/industries")
def get_industries_by_sector(sector: str):
    try:
        industries = yf.Sector(sector).industries
        return {"sector": sector, "industries": industries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
/yf/history/{symbol} ✅ 

/yf/info/{symbol} ✅

/yf/actions/{symbol} ✅

/yf/dividends/{symbol} ✅

/yf/splits/{symbol}  ✅

/yf/financials/{symbol} ✅

/yf/balance-sheet/{symbol}  ✅

/yf/cashflow/{symbol} ✅

/yf/sustainability/{symbol} ✅

/yf/recommendations/{symbol} ✅

/yf/calendar/{symbol} ✅

/yf/options/{symbol} ✅

/yf/isin/{symbol}  ✅ -

/yf/news/{symbol}  ✅

/yf/major-holders/{symbol} ✅

/yf/institutional-holders/{symbol} ✅

/yf/mutualfund-holders/{symbol} ✅
"""