from typing import Optional
from pydantic import BaseModel

# Common base class for shared fields across all instruments
class CommonFilters(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    exchange: Optional[str] = None

# Equities filters
class EquityFilters(CommonFilters):
    currency: Optional[str] = None
    summary: Optional[str] = None
    sector: Optional[str] = None
    industry_group: Optional[str] = None
    industry: Optional[str] = None
    market: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    zipcode: Optional[str] = None
    website: Optional[str] = None
    market_cap: Optional[str] = None
    isin: Optional[str] = None
    cusip: Optional[str] = None
    figi: Optional[str] = None
    composite_figi: Optional[str] = None
    shareclass_figi: Optional[str] = None

# Currency filters
class CurrencyFilters(CommonFilters):
    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None
    summary: Optional[str] = None

# Crypto filters
class CryptoFilters(CommonFilters):
    cryptocurrency: Optional[str] = None
    currency: Optional[str] = None
    summary: Optional[str] = None

# ETF filters
class ETFFilters(CommonFilters):
    currency: Optional[str] = None
    summary: Optional[str] = None
    category_group: Optional[str] = None
    category: Optional[str] = None
    family: Optional[str] = None

# Fund filters
class FundFilters(CommonFilters):
    currency: Optional[str] = None
    summary: Optional[str] = None
    category_group: Optional[str] = None
    category: Optional[str] = None
    family: Optional[str] = None

# Index filters
class IndexFilters(CommonFilters):
    currency: Optional[str] = None
    summary: Optional[str] = None
    category_group: Optional[str] = None
    category: Optional[str] = None

# Money market filters
class MoneymarketFilters(CommonFilters):
    currency: Optional[str] = None
    summary: Optional[str] = None
    category_group: Optional[str] = None
    category: Optional[str] = None
    family: Optional[str] = None
