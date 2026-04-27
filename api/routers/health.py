from fastapi import APIRouter

from ..config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "env": settings.app_env,
        "version": settings.app_version,
    }