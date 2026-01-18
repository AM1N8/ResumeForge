"""
Database models for the resume structuring agent.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UploadStatus(str, Enum):
    """Status of resume upload processing."""

    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    STRUCTURING = "structuring"
    COMPLETED = "completed"
    FAILED = "failed"


class ResumeUpload(Base):
    """Model for uploaded resume files."""

    __tablename__ = "resume_uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # pdf, md, tex
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # bytes
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[UploadStatus] = mapped_column(
        SQLEnum(UploadStatus), default=UploadStatus.PENDING, nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship to structured resume
    structured_resume: Mapped[Optional["StructuredResume"]] = relationship(
        back_populates="resume_upload"
    )


class GitHubData(Base):
    """Model for cached GitHub profile and repository data."""

    __tablename__ = "github_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    profile_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    repositories: Mapped[list] = mapped_column(JSON, nullable=False)
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    cache_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationship to structured resume
    structured_resume: Mapped[Optional["StructuredResume"]] = relationship(
        back_populates="github_data"
    )


class StructuredResume(Base):
    """Model for final structured resume output."""

    __tablename__ = "structured_resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_upload_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("resume_uploads.id"), nullable=True
    )
    github_data_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("github_data.id"), nullable=True
    )

    # Structured resume data stored as JSON
    contact: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    technical_skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    projects: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    education: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    experience: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    certifications: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    additional_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    resume_upload: Mapped[Optional["ResumeUpload"]] = relationship(back_populates="structured_resume")
    github_data: Mapped[Optional["GitHubData"]] = relationship(back_populates="structured_resume")
    decision_log: Mapped[Optional["DecisionLog"]] = relationship(back_populates="structured_resume")


class DecisionLog(Base):
    """Model for storing LLM decision explanations."""

    __tablename__ = "decision_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    structured_resume_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("structured_resumes.id"), nullable=False
    )
    decisions: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship
    structured_resume: Mapped["StructuredResume"] = relationship(back_populates="decision_log")
