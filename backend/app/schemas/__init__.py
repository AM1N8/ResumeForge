"""Schemas module."""

from app.schemas.resume_schema import (
    CanonicalResume,
    Certification,
    ContactInfo,
    DecisionLogEntry,
    Education,
    Experience,
    LLMStructuredOutput,
    Project,
    TechnicalSkills,
)
from app.schemas.api_schemas import (
    ErrorDetail,
    ErrorResponse,
    ExportRequest,
    ExportResponse,
    GitHubFetchRequest,
    GitHubFetchResponse,
    GitHubProfileSummary,
    GitHubRepoSummary,
    HealthResponse,
    ResumeUploadDetail,
    ResumeUploadResponse,
    StructuredResumeResponse,
    StructureRequest,
    StructureResponse,
)

__all__ = [
    # Resume schema
    "CanonicalResume",
    "Certification",
    "ContactInfo",
    "DecisionLogEntry",
    "Education",
    "Experience",
    "LLMStructuredOutput",
    "Project",
    "TechnicalSkills",
    # API schemas
    "ErrorDetail",
    "ErrorResponse",
    "ExportRequest",
    "ExportResponse",
    "GitHubFetchRequest",
    "GitHubFetchResponse",
    "GitHubProfileSummary",
    "GitHubRepoSummary",
    "HealthResponse",
    "ResumeUploadDetail",
    "ResumeUploadResponse",
    "StructuredResumeResponse",
    "StructureRequest",
    "StructureResponse",
]
