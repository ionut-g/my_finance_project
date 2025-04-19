import json
from financedatabase import Equities, Currencies, Cryptos, ETFs, Funds, Indices, Moneymarkets
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_to_json(df, filename):
    filepath = DATA_DIR / filename

    df.replace({np.nan: None, np.inf: None, -np.inf: None}, inplace=True)
    df = df[df.index.notna()]
    df.index = df.index.astype(str)

    # Convert to dict and inject symbol field
    df_dict = df.to_dict(orient="index")
    for symbol in df_dict:
        df_dict[symbol]["symbol"] = symbol

    with open(filepath, "w") as f:
        json.dump(df_dict, f, indent=2, allow_nan=False)

    print(f"✅ Saved {len(df_dict)} entries to {filename}")

if __name__ == "__main__":
    instruments = [
        (Equities, "Equities"),
        (Currencies, "Currencies"),
        (Cryptos, "Cryptos"),
        (ETFs, "ETFs"),
        (Funds, "Funds"),
        (Indices, "Indices"),
        (Moneymarkets, "Moneymarkets"),
    ]

    for model, name in instruments:
        save_to_json(model().select(), f"all_{name}.json")
