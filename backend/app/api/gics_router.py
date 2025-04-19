from fastapi import APIRouter
from app.services.gics_service import get_all_sectors

router = APIRouter()

@router.get("/sectors")
def list_sectors():
    return get_all_sectors()
