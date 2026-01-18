"""
Health check endpoint.
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.api_schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check API health status.
    Returns current status, version, and timestamp.
    """
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
    )
