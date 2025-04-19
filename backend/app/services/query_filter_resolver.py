from fastapi import HTTPException
from app.models.query_filters import (
    EquityFilters,
    CurrencyFilters,
    CryptoFilters,
    ETFFilters,
    FundFilters,
    IndexFilters,
    MoneymarketFilters
)

FILTER_MAP = {
    "equities": EquityFilters,
    "currencies": CurrencyFilters,
    "cryptos": CryptoFilters,
    "etfs": ETFFilters,
    "funds": FundFilters,
    "indices": IndexFilters,
    "moneymarkets": MoneymarketFilters
}

def get_filter_model(instrument_type: str):
    try:
        return FILTER_MAP[instrument_type.lower()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unsupported instrument type '{instrument_type}'")
