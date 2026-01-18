"""
Data normalization service for pre-processing resume data.
"""

import re
from typing import List, Set

from app.core.logging import get_logger

logger = get_logger(__name__)


class NormalizationService:
    """Service for normalizing and cleaning resume data."""

    # Technology name mappings (lowercase key -> normalized value)
    TECHNOLOGY_ALIASES: dict[str, str] = {
        # Programming Languages
        "python3": "Python",
        "python2": "Python",
        "py": "Python",
        "javascript": "JavaScript",
        "js": "JavaScript",
        "typescript": "TypeScript",
        "ts": "TypeScript",
        "c++": "C++",
        "cpp": "C++",
        "c#": "C#",
        "csharp": "C#",
        "golang": "Go",
        "go": "Go",
        "rust": "Rust",
        "java": "Java",
        "kotlin": "Kotlin",
        "swift": "Swift",
        "ruby": "Ruby",
        "php": "PHP",
        "r": "R",
        "matlab": "MATLAB",
        "scala": "Scala",
        "perl": "Perl",
        "shell": "Shell",
        "bash": "Bash",
        "powershell": "PowerShell",
        "sql": "SQL",
        "html": "HTML",
        "css": "CSS",
        "sass": "Sass",
        "scss": "SCSS",
        "less": "LESS",

        # Frontend Frameworks
        "react": "React",
        "react.js": "React",
        "reactjs": "React",
        "react js": "React",
        "vue": "Vue.js",
        "vue.js": "Vue.js",
        "vuejs": "Vue.js",
        "angular": "Angular",
        "angularjs": "Angular",
        "svelte": "Svelte",
        "next": "Next.js",
        "next.js": "Next.js",
        "nextjs": "Next.js",
        "nuxt": "Nuxt.js",
        "nuxt.js": "Nuxt.js",
        "gatsby": "Gatsby",

        # Backend Frameworks
        "node": "Node.js",
        "node.js": "Node.js",
        "nodejs": "Node.js",
        "express": "Express.js",
        "express.js": "Express.js",
        "expressjs": "Express.js",
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "spring": "Spring",
        "spring boot": "Spring Boot",
        "rails": "Ruby on Rails",
        "ruby on rails": "Ruby on Rails",
        "laravel": "Laravel",
        "asp.net": "ASP.NET",
        "aspnet": "ASP.NET",

        # Databases
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "mysql": "MySQL",
        "mariadb": "MariaDB",
        "mongo": "MongoDB",
        "mongodb": "MongoDB",
        "redis": "Redis",
        "sqlite": "SQLite",
        "dynamodb": "DynamoDB",
        "cassandra": "Cassandra",
        "elasticsearch": "Elasticsearch",
        "neo4j": "Neo4j",

        # Cloud & DevOps
        "aws": "AWS",
        "amazon web services": "AWS",
        "gcp": "Google Cloud Platform",
        "google cloud": "Google Cloud Platform",
        "azure": "Azure",
        "docker": "Docker",
        "docker-compose": "Docker Compose",
        "kubernetes": "Kubernetes",
        "k8s": "Kubernetes",
        "terraform": "Terraform",
        "ansible": "Ansible",
        "jenkins": "Jenkins",
        "circleci": "CircleCI",
        "travis": "Travis CI",
        "github actions": "GitHub Actions",
        "gitlab ci": "GitLab CI",

        # Tools
        "git": "Git",
        "github": "GitHub",
        "gitlab": "GitLab",
        "bitbucket": "Bitbucket",
        "vscode": "VS Code",
        "visual studio code": "VS Code",
        "vim": "Vim",
        "neovim": "Neovim",
        "postman": "Postman",
        "figma": "Figma",
        "jira": "Jira",
        "confluence": "Confluence",
        "slack": "Slack",
        "notion": "Notion",

        # ML/AI
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "keras": "Keras",
        "scikit-learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "matplotlib": "Matplotlib",
        "opencv": "OpenCV",
        "huggingface": "Hugging Face",
        "langchain": "LangChain",

        # Testing
        "jest": "Jest",
        "mocha": "Mocha",
        "pytest": "pytest",
        "junit": "JUnit",
        "cypress": "Cypress",
        "selenium": "Selenium",
        "playwright": "Playwright",
    }

    def normalize_technology(self, tech: str) -> str:
        """Normalize a single technology name."""
        # Clean whitespace
        tech = tech.strip()

        # Check for exact match (case-insensitive)
        lookup = tech.lower()
        if lookup in self.TECHNOLOGY_ALIASES:
            return self.TECHNOLOGY_ALIASES[lookup]

        # If not found, return with proper capitalization
        # Handle common patterns
        if tech.lower() == tech:
            # All lowercase - capitalize first letter of each word
            return tech.title()

        # Return as-is if already has mixed case
        return tech

    def normalize_technologies(self, technologies: List[str]) -> List[str]:
        """Normalize a list of technology names and remove duplicates."""
        seen: Set[str] = set()
        normalized: List[str] = []

        for tech in technologies:
            normalized_tech = self.normalize_technology(tech)
            if normalized_tech.lower() not in seen:
                seen.add(normalized_tech.lower())
                normalized.append(normalized_tech)

        return normalized

    def deduplicate_skills(
        self,
        languages: List[str],
        frameworks: List[str],
        tools: List[str],
        databases: List[str],
        other: List[str],
    ) -> dict[str, List[str]]:
        """
        Deduplicate skills across categories.
        Skills are kept in the first category they appear in.
        """
        seen: Set[str] = set()
        result = {"languages": [], "frameworks": [], "tools": [], "databases": [], "other": []}

        categories = [
            ("languages", languages),
            ("frameworks", frameworks),
            ("databases", databases),
            ("tools", tools),
            ("other", other),
        ]

        for category_name, skills in categories:
            for skill in skills:
                normalized = self.normalize_technology(skill)
                if normalized.lower() not in seen:
                    seen.add(normalized.lower())
                    result[category_name].append(normalized)

        return result

    def normalize_date(self, date_str: str) -> str:
        """Normalize date string to consistent format."""
        if not date_str:
            return date_str

        date_str = date_str.strip()

        # Already in good format
        if re.match(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$", date_str):
            return date_str

        # Handle "Present" or "Current"
        if date_str.lower() in ["present", "current", "now", "ongoing"]:
            return "Present"

        # Handle MM/YYYY or MM-YYYY
        match = re.match(r"^(\d{1,2})[/-](\d{4})$", date_str)
        if match:
            month_num, year = int(match.group(1)), match.group(2)
            months = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            if 1 <= month_num <= 12:
                return f"{months[month_num - 1]} {year}"

        # Handle YYYY-MM
        match = re.match(r"^(\d{4})-(\d{1,2})$", date_str)
        if match:
            year, month_num = match.group(1), int(match.group(2))
            months = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            if 1 <= month_num <= 12:
                return f"{months[month_num - 1]} {year}"

        # Return as-is if can't parse
        return date_str

    def clean_text(self, text: str) -> str:
        """Clean up text by removing extra whitespace and encoding issues."""
        if not text:
            return text

        # Normalize unicode
        text = text.replace("\u2019", "'")
        text = text.replace("\u2018", "'")
        text = text.replace("\u201c", '"')
        text = text.replace("\u201d", '"')
        text = text.replace("\u2013", "-")
        text = text.replace("\u2014", "-")
        text = text.replace("\u2022", "•")

        # Normalize whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def remove_sensitive_info(self, text: str) -> str:
        """Remove potentially sensitive information from text."""
        # Remove SSN patterns
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED]", text)

        # Remove passport numbers (common formats)
        text = re.sub(r"\b[A-Z]{2}\d{7}\b", "[REDACTED]", text)

        # Remove credit card patterns
        text = re.sub(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "[REDACTED]", text)

        return text
