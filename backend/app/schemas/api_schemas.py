"""
Pydantic schemas for API requests and responses.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.resume import UploadStatus
from app.schemas.resume_schema import (
    CanonicalResume,
    DecisionLogEntry,
)


# =============================================================================
# Health Check
# =============================================================================


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str = "0.1.0"
    timestamp: datetime


# =============================================================================
# Resume Upload
# =============================================================================


class ResumeUploadResponse(BaseModel):
    """Response after uploading a resume."""

    upload_id: int
    filename: str
    file_type: str
    file_size: int
    status: UploadStatus
    text_preview: Optional[str] = Field(None, description="First 500 chars of extracted text")
    created_at: datetime


class ResumeUploadDetail(ResumeUploadResponse):
    """Detailed resume upload with full text."""

    raw_text: Optional[str] = None
    error_message: Optional[str] = None


# =============================================================================
# GitHub
# =============================================================================


class GitHubFetchRequest(BaseModel):
    """Request to fetch GitHub data."""

    username: str = Field(..., min_length=1, max_length=100, description="GitHub username")


class GitHubProfileSummary(BaseModel):
    """Summary of GitHub profile."""

    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    public_repos: int = 0
    followers: int = 0


class GitHubRepoSummary(BaseModel):
    """Summary of a GitHub repository."""

    name: str
    description: Optional[str] = None
    url: str
    languages: List[str] = Field(default_factory=list)
    stars: int = 0
    forks: int = 0
    updated_at: str


class GitHubFetchResponse(BaseModel):
    """Response after fetching GitHub data."""

    github_data_id: int
    profile: GitHubProfileSummary
    repository_count: int
    top_repositories: List[GitHubRepoSummary] = Field(default_factory=list)
    cached: bool = False


# =============================================================================
# Resume Structuring
# =============================================================================


class StructuringSettings(BaseModel):
    """Settings for resume structuring and styling."""
    
    project_count: int = Field(3, ge=1, le=10, description="Number of projects to include")
    resume_language: str = Field("English", description="Language for the output resume")
    verbosity: str = Field("Standard", description="Concise, Standard, or Detailed")
    primary_color: str = Field("blue", description="Primary accent color name or hex")


class StructureRequest(BaseModel):
    """Request to structure a resume."""

    resume_upload_id: Optional[int] = Field(None, description="ID of uploaded resume")
    github_data_id: Optional[int] = Field(None, description="ID of fetched GitHub data")
    custom_instructions: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional custom instructions for AI to follow when structuring the resume"
    )
    settings: Optional[StructuringSettings] = Field(None, description="Optional structuring and styling settings")


class StructureResponse(BaseModel):
    """Response after structuring a resume."""

    structured_resume_id: int
    status: str = "completed"
    message: str = "Resume structured successfully"


class StructuredResumeResponse(BaseModel):
    """Full structured resume response."""

    id: int
    resume: CanonicalResume
    decision_log: List[DecisionLogEntry] = Field(default_factory=list)
    sources: dict = Field(default_factory=dict)  # {"resume": bool, "github": bool}
    updated_at: datetime


class ResumeSummaryItem(BaseModel):
    """Summary item for resume list."""
    
    id: int
    name: str = "Unknown"
    summary: Optional[str] = None
    created_at: datetime


class ResumeListResponse(BaseModel):
    """List of structured resumes."""
    
    items: List[ResumeSummaryItem] = Field(default_factory=list)


# =============================================================================
# Export
# =============================================================================


class ExportRequest(BaseModel):
    """Request to export a resume."""

    format: str = Field("markdown", description="Export format: markdown, json")


class ExportResponse(BaseModel):
    """Response with exported resume content."""

    format: str
    content: str
    filename: str


# =============================================================================
# Error Response
# =============================================================================


class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: str
    message: str
    details: Optional[str] = None
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: ErrorDetail
