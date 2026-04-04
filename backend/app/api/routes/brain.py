"""Brain activation endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def brain_health():
    """Verify brain service is operational."""
    return {"status": "ok", "service": "brain"}