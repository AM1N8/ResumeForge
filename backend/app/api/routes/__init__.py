"""API routes module."""

from app.api.routes.health import router as health_router
from app.api.routes.github import router as github_router
from app.api.routes.resume import router as resume_router

__all__ = ["health_router", "github_router", "resume_router"]
