from fastapi import FastAPI
from app.api import gics_router

app = FastAPI(title="Finance Bot API")

app.include_router(gics_router.router,  prefix="/gics", tags=["GICS"])

@app.get("/")
def root():
    return {"message": "Finance boot backend is running"}