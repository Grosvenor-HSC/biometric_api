# health.py — generated placeholder
from fastapi import APIRouter
router = APIRouter(tags=["health"])

@router.get("/health")
def health_root():
    return {"status": "ok"}

@router.get("/api/health")
def health_api():
    return {"status": "ok"}
