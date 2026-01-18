"""
LLM service using Groq API for resume structuring.
"""

import json
from pathlib import Path
from typing import Any, Optional

from groq import Groq

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.utils import sanitize_text
from app.schemas.resume_schema import CanonicalResume, DecisionLogEntry, LLMStructuredOutput

logger = get_logger(__name__)


class LLMService:
    """Service for LLM-based resume structuring using Groq."""

    def __init__(self):
        """Initialize Groq client."""
        settings = get_settings()
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.temperature = settings.groq_temperature
        self.max_tokens = settings.groq_max_tokens
        self._system_prompt: Optional[str] = None

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        if self._system_prompt is not None:
            return self._system_prompt

        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "system_prompt.txt"

        if prompt_path.exists():
            self._system_prompt = prompt_path.read_text(encoding="utf-8")
        else:
            # Fallback to inline prompt
            self._system_prompt = self._get_default_system_prompt()

        return self._system_prompt

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt if file not found."""
        return """You are a professional resume structuring assistant specializing in internship applications.
Your role is to transform unstructured resume data and GitHub information into a clean, well-organized canonical resume format.

CRITICAL RULES:
1. NEVER fabricate or invent information
2. ONLY use data explicitly provided in the input
3. If information is missing, leave fields empty or null
4. Maintain factual accuracy at all costs
5. Do not make assumptions about dates, locations, or achievements

You must return a valid JSON object with two keys:
1. "structured_resume" - The formatted resume following the canonical schema
2. "decision_log" - Array of decisions explaining your choices

For the structured_resume, use this exact structure:
{
  "contact": {"full_name": "", "email": "", "phone": null, "location": null, "github": null, "linkedin": null, "website": null},
  "summary": "",
  "technical_skills": {"languages": [], "frameworks_libraries": [], "tools_platforms": [], "databases": [], "other": []},
  "projects": [{"name": "", "description": "", "technologies": [], "source": "resume|github|both", "url": null, "highlights": [], "start_date": null, "end_date": null}],
  "education": [{"degree": "", "institution": "", "location": null, "graduation_date": null, "gpa": null, "relevant_coursework": [], "honors": []}],
  "experience": [{"role": "", "organization": "", "location": null, "start_date": "", "end_date": "", "description": [], "technologies": []}],
  "certifications": [],
  "additional_info": null
}

NORMALIZATION RULES:
- Technology names: Use official capitalization (Python, JavaScript, React, Node.js)
- Common mappings: react/react.js → React, python3 → Python, js → JavaScript
- Dates: Use "Month YYYY" or "YYYY" format

PROJECT SELECTION:
- Include 5-8 most relevant projects
- Prioritize recent, well-documented projects with clear impact
- Exclude basic tutorials and homework assignments

DECISION LOG FORMAT:
Each entry should have: section, action (included/excluded/merged/normalized), items, reason, source (resume/github/both), confidence (high/medium/low)"""

    def _build_user_prompt(
        self,
        resume_text: Optional[str],
        github_data: Optional[dict[str, Any]],
        custom_instructions: Optional[str] = None,
        settings: Optional[Any] = None,
    ) -> str:
        """Build user prompt from input sources and settings."""
        parts = []
        parts.append("Please structure the following data into a canonical resume.")
        parts.append("")

        # Resume section
        parts.append("<unstructured_resume>")
        if resume_text:
            parts.append(sanitize_text(resume_text).strip())
        else:
            parts.append("Not provided")
        parts.append("</unstructured_resume>")
        parts.append("")

        # GitHub section
        parts.append("<github_data>")
        if github_data:
            # Profile
            profile = github_data.get("profile", {})
            parts.append("PROFILE:")
            parts.append(f"  Username: {profile.get('username', 'N/A')}")
            parts.append(f"  Name: {sanitize_text(profile.get('name', 'N/A'))}")
            parts.append(f"  Bio: {sanitize_text(profile.get('bio', 'N/A'))}")
            parts.append(f"  Location: {sanitize_text(profile.get('location', 'N/A'))}")
            parts.append(f"  Email: {profile.get('email', 'N/A')}")
            parts.append("")

            # Repositories
            repos = github_data.get("repositories", [])
            parts.append(f"REPOSITORIES ({len(repos)} total):")
            for i, repo in enumerate(repos, 1):
                parts.append(f"{i}. {repo['name']}")
                parts.append(f"   Description: {sanitize_text(repo.get('description')) or 'No description'}")
                parts.append(f"   Languages: {', '.join(repo.get('languages', []))}")
                parts.append(f"   URL: {repo.get('url', 'N/A')}")
                parts.append(f"   Stars: {repo.get('stars', 0)}")
                if repo.get("readme"):
                    # Sanitize and truncate
                    readme = sanitize_text(repo["readme"])
                    parts.append(f"   README: {readme[:500]}")
                parts.append("")
        else:
            parts.append("Not provided")
        parts.append("</github_data>")
        parts.append("")

        # Add custom instructions if provided
        if custom_instructions:
            parts.append("<custom_instructions>")
            parts.append(custom_instructions.strip())
            parts.append("</custom_instructions>")
            parts.append("")

            parts.append("</custom_instructions>")
            parts.append("")

        parts.append("GOAL: Extract and normalize information from the tags above into the JSON schema.")
        parts.append("RULES:")
        parts.append("1. Use only the provided information.")
        
        # Apply settings
        if settings:
            parts.append(f"2. Write the resume content in {settings.resume_language}.")
            parts.append(f"3. Use a {settings.verbosity} writing style.")
            parts.append(f"4. Select exactly {settings.project_count} of the most relevant projects.")
        else:
            parts.append("2. Include 5-8 most relevant projects.")

        if custom_instructions:
            parts.append("5. Follow the custom instructions provided above.")

        return "\n".join(parts)

    async def structure_resume(
        self,
        resume_text: Optional[str] = None,
        github_data: Optional[dict[str, Any]] = None,
        custom_instructions: Optional[str] = None,
        settings: Optional[Any] = None,
    ) -> tuple[CanonicalResume, list[DecisionLogEntry]]:
        """
        Structure resume data using LLM.

        Args:
            resume_text: Extracted text from resume file
            github_data: Fetched GitHub profile and repo data

        Returns:
            Tuple of (CanonicalResume, list of DecisionLogEntry)
        """
        if not resume_text and not github_data:
            raise ValueError("At least one data source (resume or GitHub) must be provided")

        system_prompt = self._load_system_prompt()
        system_prompt = self._load_system_prompt()
        user_prompt = self._build_user_prompt(resume_text, github_data, custom_instructions, settings)

        logger.info(
            "calling_llm",
            model=self.model,
            has_resume=bool(resume_text),
            has_github=bool(github_data),
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                # Disabled JSON mode to allow robust extraction of JSON from conversational text
                # response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            logger.info("llm_response_received", tokens=response.usage.total_tokens)

        except Exception as e:
            logger.error("llm_api_error", error=str(e))
            raise ValueError(f"LLM API error: {str(e)}")

        # Parse and validate response
        # Clean response content (strip markdown backticks if present)
        clean_content = content.strip()
        if clean_content.startswith("```json"):
            clean_content = clean_content[7:]
        if clean_content.endswith("```"):
            clean_content = clean_content[:-3]
        clean_content = clean_content.strip()

        return self._parse_response(clean_content)

    def _parse_response(
        self,
        content: str,
    ) -> tuple[CanonicalResume, list[DecisionLogEntry]]:
        """Parse and validate LLM response."""
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            logger.info("attempting_json_repair", content_preview=content[:200])
            try:
                parsed = self._attempt_json_repair(content)
            except ValueError as ve:
                logger.error("json_parse_failed", error=str(ve), raw_content=content)
                raise

        # Normalize field names to handle LLM variations
        try:
            self._normalize_schema(parsed)
            
            # Validate structured resume
            resume_data = parsed.get("structured_resume", {})
            structured_resume = CanonicalResume(**resume_data)

            # Parse decision log
            decision_log_data = parsed.get("decision_log", [])
            decision_log = []
            for entry in decision_log_data:
                try:
                    decision_log.append(DecisionLogEntry(**entry))
                except Exception as e:
                    logger.warning("invalid_decision_entry", entry=entry, error=str(e))

            return structured_resume, decision_log

        except Exception as e:
            logger.error("schema_validation_error", error=str(e), parsed_data=parsed)
            raise ValueError(f"LLM response does not match expected schema: {str(e)}")

    def _normalize_schema(self, data: dict[str, Any]) -> None:
        """
        Normalize field names in the LLM response to handle common variations.
        Common issues: 'title' instead of 'role', 'company' instead of 'organization', etc.
        """
        resume = data.get("structured_resume", {})
        if not resume:
            return

        # Handle Experience entries
        experience_list = resume.get("experience", [])
        if isinstance(experience_list, list):
            for entry in experience_list:
                if not isinstance(entry, dict):
                    continue
                # role aliases
                if "role" not in entry and "title" in entry:
                    entry["role"] = entry.pop("title")
                # organization aliases
                if "organization" not in entry and "company" in entry:
                    entry["organization"] = entry.pop("company")
                # description aliases (handle if string instead of list)
                if "description" in entry and isinstance(entry["description"], str):
                    entry["description"] = [entry["description"]]

        # Handle Education entries
        education_list = resume.get("education", [])
        if isinstance(education_list, list):
            for entry in education_list:
                if not isinstance(entry, dict):
                    continue
                # institution aliases
                if "institution" not in entry and "school" in entry:
                    entry["institution"] = entry.pop("school")
                if "institution" not in entry and "university" in entry:
                    entry["institution"] = entry.pop("university")

        # Handle Project entries
        projects_list = resume.get("projects", [])
        if isinstance(projects_list, list):
            for entry in projects_list:
                if not isinstance(entry, dict):
                    continue
                # highlights aliases
                if "highlights" not in entry and "achievements" in entry:
                    entry["highlights"] = entry.pop("achievements")
                if "highlights" not in entry and "bullets" in entry:
                    entry["highlights"] = entry.pop("bullets")

    def _attempt_json_repair(self, content: str) -> dict[str, Any]:
        """Attempt to repair common JSON issues and extract nested objects."""
        # Try to find the start of the actual structured resume object
        # The model sometimes leaks prompt headers like "Competition" or tags
        # before starting the actual JSON we want.
        
        markers = [
            '{"structured_resume":',
            '"structured_resume":',
            '{',
        ]
        
        for marker in markers:
            start = content.find(marker)
            if start == -1:
                continue
            
            # If we found a marker, try to find the corresponding closing brace
            # starting from the end
            end = content.rfind("}") + 1
            if end > start:
                try:
                    # If marker was "structured_resume":, we need to wrap it in {}
                    candidate = content[start:end]
                    if not candidate.startswith("{"):
                        candidate = "{" + candidate
                    
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue
                    
        raise ValueError("Could not extract valid JSON from LLM response")
