import yfinance as yf

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

def get_all_sectors():
    return sectors_keys

def get_industries_by_sector(sector: str):
        industries = yf.Sector(sector).industries
        return {"sector": sector, "industries": industries}
   
print(get_industries_by_sector("utilities"))