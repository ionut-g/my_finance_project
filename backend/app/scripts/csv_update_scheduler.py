from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pathlib import Path
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("csv_updater")

CACHE_DIR = Path(__file__).parent / ".." / "data" / "yfinance_cache"
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

def update_csv(file_path: Path):
    try:
        logger.info(f"\n🔄 Checking file: {file_path.name}")
        symbol, interval_ext = file_path.stem.split("_", 1)
        interval = interval_ext
        max_window = INTERVAL_WINDOWS.get(interval, timedelta(days=7))

        df_existing = pd.read_csv(file_path, index_col=0, parse_dates=True)
        df_existing.index = pd.to_datetime(df_existing.index, errors="coerce")
        df_existing = df_existing[~df_existing.index.isna()]

        last_date = df_existing.index.max()
        now = datetime.utcnow()
        fetch_from = last_date + timedelta(minutes=1)
        fetch_to = now

        logger.info(f"⏳ Downloading {symbol} from {fetch_from} to {fetch_to} ({interval})")
        df_new = yf.download(
            symbol,
            start=fetch_from,
            end=fetch_to,
            interval=interval,
            progress=False,
            threads=False
        )

        if df_new is not None and not df_new.empty:
            df_new.index = pd.to_datetime(df_new.index)
            df_all = pd.concat([df_existing, df_new])
            df_all = df_all[~df_all.index.duplicated(keep="last")]
            df_all.sort_index(inplace=True)
            df_all.to_csv(file_path)
            logger.info(f"✅ Updated {file_path.name} with {len(df_new)} new rows")
        else:
            logger.info(f"✅ No new data for {symbol} ({interval})")

    except Exception as e:
        logger.error(f"❌ Failed to update {file_path.name}: {e}")

def scan_and_update():
    csv_files = CACHE_DIR.glob("*.csv")
    for csv_file in csv_files:
        update_csv(csv_file)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(scan_and_update, IntervalTrigger(minutes=1))
    scheduler.start()

    logger.info("🚀 CSV auto-updater started. Running every 1 minute...")

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("🛑 Scheduler stopped.")
