from fastapi import APIRouter, HTTPException
from app.services.local_symbol_service import load_symbols

router = APIRouter()

@router.get("/filters/{instrument_type}")
def get_filter_keys(instrument_type: str):
    try:
        data = load_symbols(instrument_type)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Instrument type not found")

    if not data:
        return {"type": instrument_type, "fields": []}

    # Preluăm primul item din dict pentru a extrage cheile
    first_item = next(iter(data.values()))
    field_names = sorted(first_item.keys())

    return {
        "type": instrument_type,
        "fields": field_names
    }
