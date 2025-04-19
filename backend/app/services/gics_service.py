import json
from pathlib import Path

GICS_FILE = Path(__file__).parent.parent / "data" / "gics.json"

def get_all_sectors():
    with open(GICS_FILE, "r") as f:
        gics_data = json.load(f)
    sectors = sorted(set(item["sector_name"] for item in gics_data))
    return {"sectors": sectors}