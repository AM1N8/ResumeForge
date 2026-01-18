"""
Pydantic schemas for the canonical resume structure.
These schemas define the exact structure that the LLM must output.
"""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator


class ContactInfo(BaseModel):
    """Contact information section of the resume."""

    full_name: Optional[str] = Field(None, description="Full name of the candidate")
    email: Optional[EmailStr] = Field(None, description="Professional email address")
    phone: Optional[str] = Field(None, description="Phone number (e.164 format preferred)")
    location: Optional[str] = Field(None, description="City, State/Country format")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    website: Optional[str] = Field(None, description="Personal website/portfolio URL")


class TechnicalSkills(BaseModel):
    """Technical skills section with categorization."""

    languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks_libraries: List[str] = Field(
        default_factory=list, description="Frameworks and libraries"
    )
    tools_platforms: List[str] = Field(default_factory=list, description="Tools and platforms")
    databases: List[str] = Field(default_factory=list, description="Database technologies")
    other: List[str] = Field(default_factory=list, description="Other technical skills")


class Project(BaseModel):
    """Individual project entry."""

    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Brief description (1-2 sentences)")
    technologies: List[str] = Field(..., description="Technologies used in the project")
    source: str = Field(
        ..., description="Source of information: 'resume', 'github', or 'both'"
    )
    url: Optional[str] = Field(None, description="Project URL (GitHub or live demo)")
    highlights: List[str] = Field(
        default_factory=list, description="2-4 key achievements/features"
    )
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD or YYYY-MM)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD, YYYY-MM, or 'Present')")

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Ensure source is one of the allowed values."""
        allowed = {"resume", "github", "both"}
        if v.lower() not in allowed:
            raise ValueError(f"source must be one of {allowed}")
        return v.lower()


class Education(BaseModel):
    """Education entry."""

    degree: str = Field(..., description="Degree name (e.g., Bachelor of Science in Computer Science)")
    institution: str = Field(..., description="University/college name")
    location: Optional[str] = Field(None, description="Institution location")
    graduation_date: Optional[str] = Field(None, description="Graduation date (Month YYYY or YYYY)")
    gpa: Optional[str] = Field(None, description="GPA (X.XX/4.0 format)")
    relevant_coursework: List[str] = Field(
        default_factory=list, description="Relevant courses taken"
    )
    honors: List[str] = Field(default_factory=list, description="Academic honors and awards")

    @field_validator("gpa")
    @classmethod
    def validate_gpa(cls, v: Optional[str]) -> Optional[str]:
        """Basic GPA format validation."""
        if v is None:
            return v
        # Allow formats like "3.85", "3.85/4.0", "3.85 / 4.0"
        return v.strip()


class Experience(BaseModel):
    """Work experience entry."""

    role: str = Field(..., description="Job title/role")
    organization: str = Field(..., description="Company/organization name")
    location: Optional[str] = Field(None, description="Job location")
    start_date: Optional[str] = Field(None, description="Start date (Month YYYY)")
    end_date: Optional[str] = Field(None, description="End date (Month YYYY or 'Present')")
    description: List[str] = Field(..., description="2-5 achievement statements")
    technologies: List[str] = Field(
        default_factory=list, description="Technologies used in this role"
    )


class Certification(BaseModel):
    """Certification entry."""

    name: str = Field(..., description="Certification name")
    issuer: Optional[str] = Field(None, description="Issuing organization")
    date: Optional[str] = Field(None, description="Date obtained (Month YYYY)")
    credential_id: Optional[str] = Field(None, description="Credential ID/number")
    url: Optional[str] = Field(None, description="Verification URL")


class CanonicalResume(BaseModel):
    """
    The canonical resume structure.
    This is the target output format for the LLM structuring process.
    """

    contact: ContactInfo = Field(..., description="Contact information")
    summary: Optional[str] = Field(
        None, description="Professional summary (2-4 sentences)"
    )
    technical_skills: TechnicalSkills = Field(
        default_factory=TechnicalSkills, description="Technical skills by category"
    )
    projects: List[Project] = Field(default_factory=list, description="Notable projects")
    education: List[Education] = Field(default_factory=list, description="Educational background")
    experience: List[Experience] = Field(default_factory=list, description="Work experience")
    certifications: List[Certification] = Field(
        default_factory=list, description="Professional certifications"
    )
    additional_info: Optional[str] = Field(
        None, description="Additional information (clubs, languages, interests)"
    )


class DecisionLogEntry(BaseModel):
    """Individual decision log entry for explainability."""

    section: str = Field(..., description="Resume section affected")
    action: str = Field(..., description="Action taken: included, excluded, merged, normalized")
    items: List[str] = Field(..., description="Items affected by this decision")
    reason: str = Field(..., description="Explanation of the decision")
    source: str = Field(..., description="Data source: resume, github, or both")
    confidence: str = Field(..., description="Confidence level: high, medium, or low")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Ensure action is valid."""
        allowed = {"included", "excluded", "merged", "normalized"}
        if v.lower() not in allowed:
            raise ValueError(f"action must be one of {allowed}")
        return v.lower()

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: str) -> str:
        """Ensure confidence is valid."""
        allowed = {"high", "medium", "low"}
        if v.lower() not in allowed:
            raise ValueError(f"confidence must be one of {allowed}")
        return v.lower()


class LLMStructuredOutput(BaseModel):
    """Complete output structure from LLM including resume and decision log."""

    structured_resume: CanonicalResume
    decision_log: List[DecisionLogEntry] = Field(default_factory=list)
