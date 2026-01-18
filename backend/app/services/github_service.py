"""
GitHub integration service using PyGithub.
Fetches profile and repository data with smart filtering.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from github import Github, GithubException
from github.Repository import Repository

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.utils import sanitize_text

logger = get_logger(__name__)


class GitHubService:
    """Service for fetching and processing GitHub data."""

    MAX_REPOS = 15
    README_PREVIEW_LENGTH = 2000
    CACHE_DURATION_HOURS = 24

    def __init__(self):
        """Initialize GitHub client."""
        settings = get_settings()
        self.token = settings.github_token
        self.client = Github(self.token) if self.token else Github()

    async def fetch_user_data(self, username: str) -> dict[str, Any]:
        """
        Fetch GitHub profile and repository data for a user.

        Args:
            username: GitHub username

        Returns:
            Dictionary with profile and repositories data
        """
        logger.info("fetching_github_data", username=username)

        try:
            user = self.client.get_user(username)

            profile = self._extract_profile(user)
            repositories = await self._fetch_repositories(user)

            logger.info(
                "github_data_fetched",
                username=username,
                repo_count=len(repositories),
            )

            return {
                "profile": profile,
                "repositories": repositories,
            }

        except GithubException as e:
            logger.error("github_api_error", username=username, status=e.status, message=e.data)
            if e.status == 404:
                raise ValueError(f"GitHub user '{username}' not found")
            elif e.status == 403:
                raise ValueError("GitHub API rate limit exceeded. Please try again later.")
            else:
                raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")

    def _extract_profile(self, user) -> dict[str, Any]:
        """Extract profile information from GitHub user object."""
        return {
            "username": user.login,
            "name": sanitize_text(user.name),
            "bio": sanitize_text(user.bio),
            "location": sanitize_text(user.location),
            "email": user.email,
            "blog": user.blog,
            "company": user.company,
            "hireable": user.hireable,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "avatar_url": user.avatar_url,
            "html_url": user.html_url,
        }

    async def _fetch_repositories(self, user) -> list[dict[str, Any]]:
        """Fetch and filter repositories for a user."""
        all_repos = list(user.get_repos(type="owner", sort="updated"))

        # Filter repositories
        filtered_repos = [
            repo for repo in all_repos
            if self._should_include_repo(repo)
        ]

        # Sort by relevance score
        scored_repos = [
            (repo, self._calculate_repo_score(repo))
            for repo in filtered_repos
        ]
        scored_repos.sort(key=lambda x: x[1], reverse=True)

        # Take top repos
        top_repos = scored_repos[:self.MAX_REPOS]

        # Extract repo data
        return [
            await self._extract_repo_data(repo)
            for repo, _ in top_repos
        ]

    def _should_include_repo(self, repo: Repository) -> bool:
        """Determine if a repository should be included."""
        # Exclude archived repos
        if repo.archived:
            return False

        # Exclude forks (unless they have significant contributions)
        if repo.fork:
            # Could check for original contributions, but for now exclude
            return False

        # Exclude repos with no content
        if not repo.description and repo.size == 0:
            return False

        return True

    def _calculate_repo_score(self, repo: Repository) -> float:
        """Calculate a relevance score for a repository."""
        score = 0.0

        # Recency bonus (last 6 months = high score)
        if repo.pushed_at:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            pushed_at = repo.pushed_at.replace(tzinfo=None) if repo.pushed_at.tzinfo else repo.pushed_at
            days_since_update = (now - pushed_at).days
            if days_since_update < 30:
                score += 50
            elif days_since_update < 90:
                score += 30
            elif days_since_update < 180:
                score += 15

        # Stars
        score += min(repo.stargazers_count * 5, 50)

        # Forks
        score += min(repo.forks_count * 2, 20)

        # Has description
        if repo.description:
            score += 10

        # Has topics
        if repo.get_topics():
            score += 10

        # Size (not too small, not too large)
        if 10 < repo.size < 100000:
            score += 5

        return score

    async def _extract_repo_data(self, repo: Repository) -> dict[str, Any]:
        """Extract relevant data from a repository."""
        # Get languages
        try:
            languages = list(repo.get_languages().keys())
        except Exception:
            languages = [repo.language] if repo.language else []

        # Get topics
        try:
            topics = repo.get_topics()
        except Exception:
            topics = []

        # Get README content (first N chars)
        readme_content = None
        try:
            readme = repo.get_readme()
            # Decode with ignore to handle weird encodings
            content = readme.decoded_content.decode("utf-8", errors="ignore")
            readme_content = sanitize_text(content)[:self.README_PREVIEW_LENGTH]
        except Exception:
            pass

        return {
            "name": repo.name,
            "description": sanitize_text(repo.description),
            "url": repo.html_url,
            "languages": languages,
            "primary_language": repo.language,
            "topics": topics,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.pushed_at.isoformat() if repo.pushed_at else None,
            "readme": readme_content,
        }

    def get_cache_expiry(self) -> datetime:
        """Get the cache expiry time for GitHub data."""
        return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=self.CACHE_DURATION_HOURS)
