from fastapi import APIRouter, Query
from typing import Optional
from app.services.gics_service import get_all_sectors, filter_gics_data, get_gics_hierarchy

router = APIRouter()

@router.get("/sectors")
def list_sectors():
    return get_all_sectors()

@router.get("/filter")
def filter_gics(
    filter_type: str = Query(..., description="sector, industry_group, industry, sub_industry"),
    sector: Optional[str] = Query(None),
    industry_group: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    sub_industry: Optional[str] = Query(None),
):
    return filter_gics_data(filter_type, sector, industry_group, industry, sub_industry)

@router.get("/hierarchy")
def full_hierarchy():
    return get_gics_hierarchy()