"""
GitHub API endpoints.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import GitHubUserNotFoundError, GitHubAPIError
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.resume import GitHubData
from app.schemas.api_schemas import (
    GitHubFetchRequest,
    GitHubFetchResponse,
    GitHubProfileSummary,
    GitHubRepoSummary,
)
from app.services.github_service import GitHubService

logger = get_logger(__name__)
router = APIRouter()


@router.post("/fetch", response_model=GitHubFetchResponse)
async def fetch_github_data(
    request: GitHubFetchRequest,
    db: AsyncSession = Depends(get_db),
) -> GitHubFetchResponse:
    """
    Fetch GitHub profile and repository data for a user.
    
    Results are cached for 24 hours to avoid rate limiting.
    """
    username = request.username.strip()
    logger.info("github_fetch_request", username=username)

    # Check cache first
    result = await db.execute(
        select(GitHubData).where(GitHubData.username == username)
    )
    cached = result.scalar_one_or_none()

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if cached and cached.cache_expires_at > now:
        logger.info("github_cache_hit", username=username)
        return _build_response(cached, cached=True)

    # Fetch fresh data
    service = GitHubService()

    try:
        data = await service.fetch_user_data(username)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise GitHubUserNotFoundError(username)
        raise GitHubAPIError(error_msg)

    # Store/update in database
    if cached:
        cached.profile_data = data["profile"]
        cached.repositories = data["repositories"]
        cached.extracted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        cached.cache_expires_at = service.get_cache_expiry()
    else:
        cached = GitHubData(
            username=username,
            profile_data=data["profile"],
            repositories=data["repositories"],
            extracted_at=datetime.now(timezone.utc).replace(tzinfo=None),
            cache_expires_at=service.get_cache_expiry(),
        )
        db.add(cached)

    await db.flush()
    await db.refresh(cached)

    logger.info("github_data_stored", username=username, github_data_id=cached.id)

    return _build_response(cached, cached=False)


def _build_response(github_data: GitHubData, cached: bool) -> GitHubFetchResponse:
    """Build response from GitHubData model."""
    profile = github_data.profile_data
    repos = github_data.repositories

    return GitHubFetchResponse(
        github_data_id=github_data.id,
        profile=GitHubProfileSummary(
            username=profile.get("username", ""),
            name=profile.get("name"),
            bio=profile.get("bio"),
            location=profile.get("location"),
            email=profile.get("email"),
            public_repos=profile.get("public_repos", 0),
            followers=profile.get("followers", 0),
        ),
        repository_count=len(repos),
        top_repositories=[
            GitHubRepoSummary(
                name=repo["name"],
                description=repo.get("description"),
                url=repo.get("url", ""),
                languages=repo.get("languages", []),
                stars=repo.get("stars", 0),
                forks=repo.get("forks", 0),
                updated_at=repo.get("updated_at", ""),
            )
            for repo in repos[:5]
        ],
        cached=cached,
    )
