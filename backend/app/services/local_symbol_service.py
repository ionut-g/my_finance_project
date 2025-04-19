import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

VALID_TYPES = {
    "equities": "Equities",
    "currencies": "Currencies",
    "cryptos": "Cryptos",
    "etfs": "ETFs",
    "funds": "Funds",
    "indices": "Indices",
    "moneymarkets": "Moneymarkets",
}

def load_symbols(instrument_type: str) -> dict:
    from pathlib import Path
    import json

    VALID_TYPES = {
        "equities": "Equities",
        "currencies": "Currencies",
        "cryptos": "Cryptos",
        "etfs": "ETFs",
        "funds": "Funds",
        "indices": "Indices",
        "moneymarkets": "Moneymarkets",
    }

    type_key = instrument_type.lower()
    if type_key not in VALID_TYPES:
        raise FileNotFoundError(f"Invalid type '{instrument_type}'")

    filename = f"all_{VALID_TYPES[type_key]}.json"
    path = Path(__file__).parent.parent / "data" / filename

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filename}")

    with open(path, "r") as f:
        raw_data = json.load(f)

    # inject 'symbol' key into each item
    for sym, item in raw_data.items():
        item["symbol"] = sym

    return raw_data

    
def get_available_instrument_types() -> list[str]:
    return list(VALID_TYPES.keys())