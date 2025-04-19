from fastapi import APIRouter, HTTPException, Query
from app.services.local_symbol_service import load_symbols

router = APIRouter()
@router.get("/autocomplete/{instrument_type}")
def autocomplete_symbols(
    instrument_type: str,
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100)
):
    try:
        data = load_symbols(instrument_type)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Instrument type not found")

    q = q.lower()
    results = []

    for symbol, item in data.items():
        if item is None:
            continue

        name = item.get("name")
        if name and (q in symbol.lower() or q in name.lower()):
            results.append({
                "symbol": symbol,
                "name": name
            })

        if len(results) >= limit:
            break

    return results
