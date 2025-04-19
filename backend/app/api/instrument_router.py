from fastapi import APIRouter, Query, Request, HTTPException
from typing import Optional
from app.services.local_symbol_service import load_symbols, get_available_instrument_types
from app.services.query_filter_resolver import get_filter_model

router = APIRouter()

@router.get("/types")
def list_instrument_types():
    return {"available": get_available_instrument_types()}

@router.get("/{instrument_type}")
def get_instruments(
    instrument_type: str,
    request: Request,
    limit: Optional[int] = Query(None, ge=1),
    offset: int = Query(0, ge=0)
):
    # Step 1: resolve correct filter model based on instrument type
    FilterModel = get_filter_model(instrument_type)

    # Step 2: extract and validate query parameters
    query_params = dict(request.query_params)
    query_params.pop("limit", None)
    query_params.pop("offset", None)

    try:
        filters = FilterModel(**query_params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid query params: {str(e)}")

    # Step 3: load data and apply filtering
    try:
        data = load_symbols(instrument_type)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Instrument type not found")

    filtered = []
    for sym, item in data.items():
        match = True
        for key, value in filters.dict(exclude_none=True).items():
            target = sym if key == "symbol" else item.get(key)
            if value.lower() not in str(target).lower():
                match = False
                break
        if match:
            filtered.append({"symbol": sym, **item})

    results = filtered[offset:]
    if limit is not None:
        results = results[:limit]

    return {
        "type": instrument_type,
        "count": len(filtered),
        "results": results
    }
