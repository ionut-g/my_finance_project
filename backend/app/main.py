from fastapi import FastAPI
from app.api import gics_router, instrument_router, \
    instrument_filters_router, autocomplete_router, \
    yahoo_finance_router

app = FastAPI(title="Finance Bot API")

app.include_router(gics_router.router,  prefix="/gics", tags=["GICS"])
app.include_router(instrument_router.router, prefix="/instruments", tags=["Instruments"])
app.include_router(instrument_filters_router.router, prefix="/instruments", tags=["Instrument Filters"])
app.include_router(autocomplete_router.router, prefix="/instruments", tags=["Autocomplet Instruments"])
app.include_router(yahoo_finance_router.router, prefix="/yf", tags=["Historical Data from yfinance"])

@app.get("/")
def root():
    return {"message": "Finance boot backend is running"}