"""
Resume API endpoints.
"""

import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import (
    FileParsingError,
    FileTooLargeError,
    InvalidFileTypeError,
    LLMServiceError,
    ResourceNotFoundError,
    ValidationError,
)
from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.resume import (
    DecisionLog,
    GitHubData,
    ResumeUpload,
    StructuredResume,
    UploadStatus,
)
from app.schemas.api_schemas import (
    ResumeUploadResponse,
    ResumeUploadDetail,
    StructuredResumeResponse,
    StructureRequest,
    StructureResponse,
    ResumeListResponse,
    ResumeSummaryItem,
)
from app.schemas.resume_schema import CanonicalResume, DecisionLogEntry
from app.services.parsers import ParserFactory
from app.services.llm_service import LLMService

logger = get_logger(__name__)
router = APIRouter()
settings = get_settings()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> ResumeUploadResponse:
    """
    Upload and parse a resume file.
    
    Supported formats: PDF, Markdown (.md), LaTeX (.tex)
    Maximum file size: 10MB
    """
    logger.info("resume_upload_request", filename=file.filename, content_type=file.content_type)

    # Validate file type
    supported = ParserFactory.get_supported_extensions()
    if not ParserFactory.is_supported(file.filename):
        raise InvalidFileTypeError(file.filename.split(".")[-1] if file.filename else "unknown", supported)

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > settings.max_upload_size_bytes:
        raise FileTooLargeError(len(content), settings.max_upload_size_bytes)

    # Get parser and validate
    parser = ParserFactory.get_parser(file.filename)
    is_valid, error = parser.validate_file(content, file.filename)
    if not is_valid:
        raise FileParsingError(f"File validation failed: {error}")

    # Create upload record
    file_ext = file.filename.split(".")[-1].lower() if file.filename else "unknown"
    upload = ResumeUpload(
        filename=file.filename or "unknown",
        file_type=file_ext,
        file_size=len(content),
        status=UploadStatus.PARSING,
    )
    db.add(upload)
    await db.flush()

    # Parse the file
    try:
        result = await parser.parse(content, file.filename)
        upload.raw_text = result.text
        upload.status = UploadStatus.PARSED
        logger.info("resume_parsed", upload_id=upload.id, chars=result.character_count)
    except Exception as e:
        upload.status = UploadStatus.FAILED
        upload.error_message = str(e)
        await db.commit()
        raise FileParsingError(f"Failed to parse file: {str(e)}")

    await db.commit()
    await db.refresh(upload)

    return ResumeUploadResponse(
        upload_id=upload.id,
        filename=upload.filename,
        file_type=upload.file_type,
        file_size=upload.file_size,
        status=upload.status,
        text_preview=upload.raw_text[:500] if upload.raw_text else None,
        created_at=upload.created_at,
    )


@router.get("/upload/{upload_id}", response_model=ResumeUploadDetail)
async def get_upload(
    upload_id: int,
    db: AsyncSession = Depends(get_db),
) -> ResumeUploadDetail:
    """Get details of a resume upload including full extracted text."""
    result = await db.execute(
        select(ResumeUpload).where(ResumeUpload.id == upload_id)
    )
    upload = result.scalar_one_or_none()

    if not upload:
        raise ResourceNotFoundError("Resume upload", upload_id)

    return ResumeUploadDetail(
        upload_id=upload.id,
        filename=upload.filename,
        file_type=upload.file_type,
        file_size=upload.file_size,
        status=upload.status,
        text_preview=upload.raw_text[:500] if upload.raw_text else None,
        raw_text=upload.raw_text,
        error_message=upload.error_message,
        created_at=upload.created_at,
    )


@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0
) -> ResumeListResponse:
    """List structured resumes."""
    result = await db.execute(
        select(StructuredResume)
        .order_by(desc(StructuredResume.created_at))
        .limit(limit)
        .offset(offset)
    )
    resumes = result.scalars().all()
    
    items = []
    for r in resumes:
        name = "Unknown"
        if r.contact and "full_name" in r.contact:
            name = r.contact["full_name"]
            
        items.append(ResumeSummaryItem(
            id=r.id,
            name=name,
            summary=r.summary[:300] + "..." if r.summary and len(r.summary) > 300 else r.summary,
            created_at=r.created_at
        ))
    
    return ResumeListResponse(items=items)


@router.post("/structure", response_model=StructureResponse)
async def structure_resume(
    request: StructureRequest,
    db: AsyncSession = Depends(get_db),
) -> StructureResponse:
    """
    Structure a resume using LLM.
    
    Requires at least one data source (resume upload ID or GitHub data ID).
    """
    logger.info(
        "structure_request",
        resume_upload_id=request.resume_upload_id,
        github_data_id=request.github_data_id,
    )

    if not request.resume_upload_id and not request.github_data_id:
        raise ValidationError("At least one data source (resume or GitHub) must be provided")

    # Fetch resume text if provided
    resume_text: Optional[str] = None
    resume_upload: Optional[ResumeUpload] = None
    if request.resume_upload_id:
        result = await db.execute(
            select(ResumeUpload).where(ResumeUpload.id == request.resume_upload_id)
        )
        resume_upload = result.scalar_one_or_none()
        if not resume_upload:
            raise ResourceNotFoundError("Resume upload", request.resume_upload_id)
        if resume_upload.status != UploadStatus.PARSED:
            raise ValidationError(f"Resume upload is not ready: status is {resume_upload.status}")
        resume_text = resume_upload.raw_text

    # Fetch GitHub data if provided
    github_data_dict: Optional[dict] = None
    github_data: Optional[GitHubData] = None
    if request.github_data_id:
        result = await db.execute(
            select(GitHubData).where(GitHubData.id == request.github_data_id)
        )
        github_data = result.scalar_one_or_none()
        if not github_data:
            raise ResourceNotFoundError("GitHub data", request.github_data_id)
        github_data_dict = {
            "profile": github_data.profile_data,
            "repositories": github_data.repositories,
        }

    # Update resume upload status
    if resume_upload:
        resume_upload.status = UploadStatus.STRUCTURING

    # Call LLM service
    llm_service = LLMService()
    try:
        structured_resume, decision_log = await llm_service.structure_resume(
            resume_text=resume_text,
            github_data=github_data_dict,
            custom_instructions=request.custom_instructions,
            settings=request.settings,
        )
    except Exception as e:
        if resume_upload:
            resume_upload.status = UploadStatus.FAILED
            resume_upload.error_message = str(e)
        raise LLMServiceError(f"Failed to structure resume: {str(e)}")

    # Store structured resume
    structured = StructuredResume(
        resume_upload_id=request.resume_upload_id,
        github_data_id=request.github_data_id,
        contact=structured_resume.contact.model_dump() if structured_resume.contact else None,
        summary=structured_resume.summary,
        technical_skills=structured_resume.technical_skills.model_dump() if structured_resume.technical_skills else None,
        projects=[p.model_dump() for p in structured_resume.projects] if structured_resume.projects else None,
        education=[e.model_dump() for e in structured_resume.education] if structured_resume.education else None,
        experience=[e.model_dump() for e in structured_resume.experience] if structured_resume.experience else None,
        certifications=[c.model_dump() for c in structured_resume.certifications] if structured_resume.certifications else None,
        additional_info=structured_resume.additional_info,
    )
    db.add(structured)
    await db.flush()

    # Store decision log
    if decision_log:
        log = DecisionLog(
            structured_resume_id=structured.id,
            decisions=[d.model_dump() for d in decision_log],
        )
        db.add(log)

    # Update resume upload status
    if resume_upload:
        resume_upload.status = UploadStatus.COMPLETED

    await db.commit()

    logger.info("resume_structured", structured_resume_id=structured.id)

    return StructureResponse(
        structured_resume_id=structured.id,
        status="completed",
        message="Resume structured successfully",
    )


@router.get("/{resume_id}", response_model=StructuredResumeResponse)
async def get_structured_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
) -> StructuredResumeResponse:
    """Get a structured resume by ID with decision log."""
    result = await db.execute(
        select(StructuredResume).where(StructuredResume.id == resume_id)
    )
    structured = result.scalar_one_or_none()

    if not structured:
        raise ResourceNotFoundError("Structured resume", resume_id)

    # Fetch decision log
    result = await db.execute(
        select(DecisionLog).where(DecisionLog.structured_resume_id == resume_id)
    )
    decision_log = result.scalar_one_or_none()

    # Build canonical resume from stored data
    from app.schemas.resume_schema import (
        ContactInfo, TechnicalSkills, Project, Education, Experience, Certification
    )

    resume = CanonicalResume(
        contact=ContactInfo(**structured.contact) if structured.contact else ContactInfo(full_name="Unknown", email="unknown@example.com"),
        summary=structured.summary,
        technical_skills=TechnicalSkills(**structured.technical_skills) if structured.technical_skills else TechnicalSkills(),
        projects=[Project(**p) for p in structured.projects] if structured.projects else [],
        education=[Education(**e) for e in structured.education] if structured.education else [],
        experience=[Experience(**e) for e in structured.experience] if structured.experience else [],
        certifications=[Certification(**c) for c in structured.certifications] if structured.certifications else [],
        additional_info=structured.additional_info,
    )

    decision_entries = []
    if decision_log:
        for d in decision_log.decisions:
            try:
                decision_entries.append(DecisionLogEntry(**d))
            except Exception:
                pass

    return StructuredResumeResponse(
        id=structured.id,
        resume=resume,
        decision_log=decision_entries,
        sources={
            "resume": structured.resume_upload_id is not None,
            "github": structured.github_data_id is not None,
        },
        created_at=structured.created_at,
        updated_at=structured.updated_at,
    )


@router.get("/{resume_id}/export")
async def export_resume(
    resume_id: int,
    format: str = Query("markdown", description="Export format: markdown, json, or latex"),
    db: AsyncSession = Depends(get_db),
):
    """
    Export structured resume in requested format.
    
    Supported formats: markdown, json, latex
    """
    # Get the structured resume
    response = await get_structured_resume(resume_id, db)

    if format.lower() == "json":
        return response.resume.model_dump()

    elif format.lower() == "markdown":
        md = _generate_markdown(response.resume)
        return PlainTextResponse(
            content=md,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=resume_{resume_id}.md"},
        )

    elif format.lower() == "latex":
        # Get primary color from settings if available (currently settings are not stored in DB, defaulting to blue)
        # TODO: Store settings in DB to retrieve here. For now, we'll accept a query param or default.
        tex = _generate_latex(response.resume)
        return PlainTextResponse(
            content=tex,
            media_type="application/x-latex",
            headers={"Content-Disposition": f"attachment; filename=resume_{resume_id}.tex"},
        )

    else:
        raise ValidationError(f"Unsupported export format: {format}. Use 'markdown', 'json', or 'latex'.")


def _generate_markdown(resume: CanonicalResume) -> str:
    """Generate markdown from canonical resume."""
    lines = []

    # Header
    lines.append(f"# {resume.contact.full_name}")
    lines.append("")

    # Contact info
    contact_items = []
    if resume.contact.email:
        contact_items.append(f"📧 {resume.contact.email}")
    if resume.contact.phone:
        contact_items.append(f"📱 {resume.contact.phone}")
    if resume.contact.location:
        contact_items.append(f"📍 {resume.contact.location}")
    if resume.contact.github:
        contact_items.append(f"[GitHub]({resume.contact.github})")
    if resume.contact.linkedin:
        contact_items.append(f"[LinkedIn]({resume.contact.linkedin})")
    if resume.contact.website:
        contact_items.append(f"[Website]({resume.contact.website})")

    lines.append(" | ".join(contact_items))
    lines.append("")

    # Summary
    if resume.summary:
        lines.append("## Summary")
        lines.append("")
        lines.append(resume.summary)
        lines.append("")

    # Skills
    if resume.technical_skills:
        lines.append("## Technical Skills")
        lines.append("")
        skills = resume.technical_skills
        if skills.languages:
            lines.append(f"**Languages:** {', '.join(skills.languages)}")
        if skills.frameworks_libraries:
            lines.append(f"**Frameworks:** {', '.join(skills.frameworks_libraries)}")
        if skills.tools_platforms:
            lines.append(f"**Tools:** {', '.join(skills.tools_platforms)}")
        if skills.databases:
            lines.append(f"**Databases:** {', '.join(skills.databases)}")
        if skills.other:
            lines.append(f"**Other:** {', '.join(skills.other)}")
        lines.append("")

    # Projects
    if resume.projects:
        lines.append("## Projects")
        lines.append("")
        for project in resume.projects:
            title = f"### {project.name}"
            if project.url:
                title += f" ([Link]({project.url}))"
            lines.append(title)
            lines.append("")
            lines.append(project.description)
            lines.append("")
            if project.technologies:
                lines.append(f"*Technologies: {', '.join(project.technologies)}*")
            if project.highlights:
                lines.append("")
                for h in project.highlights:
                    lines.append(f"- {h}")
            lines.append("")

    # Education
    if resume.education:
        lines.append("## Education")
        lines.append("")
        for edu in resume.education:
            lines.append(f"### {edu.degree}")
            lines.append(f"**{edu.institution}**")
            if edu.graduation_date:
                lines.append(f"Graduation: {edu.graduation_date}")
            if edu.gpa:
                lines.append(f"GPA: {edu.gpa}")
            if edu.relevant_coursework:
                lines.append(f"*Coursework: {', '.join(edu.relevant_coursework)}*")
            lines.append("")

    # Experience
    if resume.experience:
        lines.append("## Experience")
        lines.append("")
        for exp in resume.experience:
            lines.append(f"### {exp.role}")
            lines.append(f"**{exp.organization}** | {exp.start_date} - {exp.end_date}")
            if exp.location:
                lines.append(f"*{exp.location}*")
            lines.append("")
            for desc in exp.description:
                lines.append(f"- {desc}")
            if exp.technologies:
                lines.append("")
                lines.append(f"*Technologies: {', '.join(exp.technologies)}*")
            lines.append("")

    # Certifications
    if resume.certifications:
        lines.append("## Certifications")
        lines.append("")
        for cert in resume.certifications:
            cert_line = f"- **{cert.name}**"
            if cert.issuer:
                cert_line += f" - {cert.issuer}"
            if cert.date:
                cert_line += f" ({cert.date})"
            lines.append(cert_line)
        lines.append("")

    # Additional Info
    if resume.additional_info:
        lines.append("## Additional Information")
        lines.append("")
        lines.append(resume.additional_info)
        lines.append("")

    return "\n".join(lines)


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters in text."""
    if not text:
        return ""
    # Order matters: escape backslash first
    replacements = [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def _generate_latex(resume: CanonicalResume, primary_color: str = "blue") -> str:
    """Generate LaTeX from canonical resume matching base resume template."""
    lines = []
    
    # Map common colors to LaTeX colors or hex
    color_map = {
        "blue": "RoyalBlue",
        "navy": "NavyBlue",
        "teal": "TealBlue",
        "maroon": "Maroon",
        "purple": "Plum",
        "black": "black"
    }
    accent_color = color_map.get(primary_color.lower(), "RoyalBlue")
    
    # Document preamble - matching base_resume template exactly
    lines.append(r"""%-------------------------
% Resume in LaTeX
% Generated by CVAgent
%-------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{multicol}
\setlength{\multicolsep}{-3.0pt}
\setlength{\columnsep}{-1pt}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.19in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.4in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries\color{""" + accent_color + r"""}
}{}{0em}{}[\color{""" + accent_color + r"""}\titlerule \vspace{-5pt}]

% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\classesList}[4]{
    \item\small{
        {#1 #2 #3 #4 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & \textbf{\small #2} \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{1.0\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{1.001\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & \textbf{\small #2}\\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemi{$\vcenter{\hbox{\tiny$\bullet$}}$}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.0in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\begin{document}
""")

    # Header with contact info
    full_name = _escape_latex(resume.contact.full_name or "Your Name")
    lines.append(r"\begin{center}")
    lines.append(rf"    {{\Huge \scshape {full_name}}} \\ \vspace{{1pt}}")
    
    # Title line (use summary first sentence or generic title)
    if resume.summary:
        # Extract profession from summary or use generic
        title = "Professional"
    else:
        title = "Professional"
    lines.append(rf"    \small \textbf{{{_escape_latex(title)}}} \\ \vspace{{5pt}}")
    
    # Contact info line
    contact_parts = []
    if resume.contact.location:
        contact_parts.append(rf"\small \faMapMarker* \hspace{{.5pt}} {_escape_latex(resume.contact.location)}")
    if resume.contact.email:
        email = _escape_latex(resume.contact.email)
        contact_parts.append(rf"\small \faEnvelope \hspace{{.5pt}} \href{{mailto:{email}}}{{\underline{{{email}}}}}")
    if resume.contact.phone:
        contact_parts.append(rf"\small \faPhone* \hspace{{.5pt}} {_escape_latex(resume.contact.phone)}")
    
    if contact_parts:
        lines.append(r"    " + " ~ \n    ".join(contact_parts) + r" \\ \vspace{3pt}")
    
    # Social links line
    social_parts = []
    if resume.contact.github:
        github_url = _escape_latex(resume.contact.github)
        github_display = resume.contact.github.replace("https://github.com/", "GitHub: ")
        social_parts.append(rf"\small \faGithub \hspace{{.5pt}} \href{{{github_url}}}{{\underline{{{_escape_latex(github_display)}}}}}")
    if resume.contact.linkedin:
        linkedin_url = _escape_latex(resume.contact.linkedin)
        social_parts.append(rf"\small \faLinkedin \hspace{{.5pt}} \href{{{linkedin_url}}}{{\underline{{LinkedIn Profile}}}}")
    if resume.contact.website:
        website_url = _escape_latex(resume.contact.website)
        social_parts.append(rf"\small \faGlobe \hspace{{.5pt}} \href{{{website_url}}}{{\underline{{Portfolio}}}}")
    
    if social_parts:
        lines.append(r"    " + " ~ \n    ".join(social_parts))
    
    lines.append(r"    \vspace{-8pt}")
    lines.append(r"\end{center}")
    lines.append("")

    # Professional Summary
    if resume.summary:
        lines.append(r"%-----------PROFESSIONAL SUMMARY-----------")
        lines.append(r"\section{Professional Summary}")
        lines.append(rf"\small{{{_escape_latex(resume.summary)}}}")
        lines.append(r"\vspace{-10pt}")
        lines.append("")

    # Education
    if resume.education:
        lines.append(r"%-----------EDUCATION-----------")
        lines.append(r"\section{Education}")
        lines.append(r"  \resumeSubHeadingListStart")
        for edu in resume.education:
            institution = _escape_latex(edu.institution)
            degree = _escape_latex(edu.degree)
            grad_date = _escape_latex(edu.graduation_date or "")
            location = _escape_latex(edu.location or "")
            lines.append(rf"    \resumeSubheading")
            lines.append(rf"      {{{institution}}}{{{grad_date}}}")
            lines.append(rf"      {{{degree}}}{{{location}}}")
            # Add honors or GPA as items if present
            if edu.gpa or edu.honors:
                lines.append(r"      \resumeItemListStart")
                if edu.gpa:
                    lines.append(rf"        \resumeItem{{GPA: {_escape_latex(edu.gpa)}}}")
                for honor in edu.honors:
                    lines.append(rf"        \resumeItem{{{_escape_latex(honor)}}}")
                lines.append(r"      \resumeItemListEnd")
        lines.append(r"  \resumeSubHeadingListEnd")
        lines.append(r"\vspace{-15pt}")
        lines.append("")

    # Technical Skills
    if resume.technical_skills:
        lines.append(r"%-----------TECHNICAL SKILLS-----------")
        lines.append(r"\section{Technical Skills}")
        lines.append(r" \begin{itemize}[leftmargin=0.15in, label={}]")
        lines.append(r"    \small{\item{")
        
        skills = resume.technical_skills
        skill_lines = []
        if skills.languages:
            skill_lines.append(rf"     \textbf{{Programming}}{{: {', '.join(skills.languages)}}}")
        if skills.frameworks_libraries:
            skill_lines.append(rf"     \textbf{{Frameworks}}{{: {', '.join(skills.frameworks_libraries)}}}")
        if skills.tools_platforms:
            skill_lines.append(rf"     \textbf{{Tools}}{{: {', '.join(skills.tools_platforms)}}}")
        if skills.databases:
            skill_lines.append(rf"     \textbf{{Databases}}{{: {', '.join(skills.databases)}}}")
        if skills.other:
            skill_lines.append(rf"     \textbf{{Other}}{{: {', '.join(skills.other)}}}")
        
        lines.append(r" \\" + r" \\".join(skill_lines))
        lines.append(r"    }}")
        lines.append(r" \end{itemize}")
        lines.append(r"\vspace{-16pt}")
        lines.append("")

    # Projects
    if resume.projects:
        lines.append(r"%-----------PROJECTS-----------")
        lines.append(r"\section{Key Projects}")
        lines.append(r"    \resumeSubHeadingListStart")
        for proj in resume.projects:
            project_name = _escape_latex(proj.name)
            project_url = proj.url or ""
            if project_url:
                project_url = _escape_latex(project_url)
                project_title = rf"\textbf{{{project_name}}} $|$ \href{{{project_url}}}{{\underline{{GitHub}}}}"
            else:
                project_title = rf"\textbf{{{project_name}}}"
            
            lines.append(r"      \resumeProjectHeading")
            lines.append(rf"          {{{project_title}}}{{}}")
            lines.append(r"          \resumeItemListStart")
            
            # Add description as first item
            if proj.description:
                lines.append(rf"            \resumeItem{{{_escape_latex(proj.description)}}}")
            
            # Add highlights
            for highlight in proj.highlights[:3]:  # Limit to 3 highlights
                lines.append(rf"            \resumeItem{{{_escape_latex(highlight)}}}")
            
            lines.append(r"          \resumeItemListEnd")
        lines.append(r"    \resumeSubHeadingListEnd")
        lines.append(r"\vspace{-15pt}")
        lines.append("")

    # Experience
    if resume.experience:
        lines.append(r"%-----------EXPERIENCE-----------")
        lines.append(r"\section{Experience \& Leadership}")
        lines.append(r"  \resumeSubHeadingListStart")
        for exp in resume.experience:
            role = _escape_latex(exp.role)
            org = _escape_latex(exp.organization)
            start = _escape_latex(exp.start_date)
            end = _escape_latex(exp.end_date)
            location = _escape_latex(exp.location or "")
            
            lines.append(r"    \resumeSubheading")
            lines.append(rf"      {{{role} -- {org}}}{{{start} -- {end}}}")
            lines.append(rf"      {{}}{{{location}}}")
            
            if exp.description:
                lines.append(r"      \resumeItemListStart")
                for desc in exp.description[:4]:  # Limit descriptions
                    lines.append(rf"        \resumeItem{{{_escape_latex(desc)}}}")
                lines.append(r"      \resumeItemListEnd")
        lines.append(r"  \resumeSubHeadingListEnd")
        lines.append(r"\vspace{-15pt}")
        lines.append("")

    # Additional Info / Languages & Interests
    if resume.additional_info:
        lines.append(r"%-----------LANGUAGES & INTERESTS-----------")
        lines.append(r"\section{Languages \& Interests}")
        lines.append(r" \begin{itemize}[leftmargin=0.15in, label={}]")
        lines.append(r"    \small{\item{")
        lines.append(rf"     \textbf{{Interests}}{{: {_escape_latex(resume.additional_info)}}}")
        lines.append(r"    }}")
        lines.append(r" \end{itemize}")
        lines.append(r"\vspace{-16pt}")
        lines.append("")

    # Document end
    lines.append(r"\end{document}")

    return "\n".join(lines)
