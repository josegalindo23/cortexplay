"""Video clips endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def clips_health():
    """Verify clips service is operational."""
    return {"status": "ok", "service": "clips"}