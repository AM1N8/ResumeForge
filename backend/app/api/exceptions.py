"""
Custom exceptions for the API.
"""

from typing import Optional


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[str] = None,
        status_code: int = 500,
    ):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(message)


class FileParsingError(AppException):
    """Error during file parsing."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            code="PARSING_FAILED",
            message=message,
            details=details,
            status_code=400,
        )


class InvalidFileTypeError(AppException):
    """Error for unsupported file types."""

    def __init__(self, file_type: str, supported: list[str]):
        super().__init__(
            code="INVALID_FILE_TYPE",
            message=f"Unsupported file type: {file_type}",
            details=f"Supported types: {', '.join(supported)}",
            status_code=400,
        )


class FileTooLargeError(AppException):
    """Error when file exceeds size limit."""

    def __init__(self, size: int, max_size: int):
        super().__init__(
            code="FILE_TOO_LARGE",
            message=f"File size ({size / 1024 / 1024:.1f}MB) exceeds maximum allowed ({max_size / 1024 / 1024:.1f}MB)",
            status_code=413,
        )


class GitHubAPIError(AppException):
    """Error from GitHub API."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            code="GITHUB_API_ERROR",
            message=message,
            details=details,
            status_code=502,
        )


class GitHubUserNotFoundError(AppException):
    """GitHub user not found."""

    def __init__(self, username: str):
        super().__init__(
            code="GITHUB_USER_NOT_FOUND",
            message=f"GitHub user '{username}' not found",
            status_code=404,
        )


class LLMServiceError(AppException):
    """Error from LLM service."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            code="LLM_ERROR",
            message=message,
            details=details,
            status_code=502,
        )


class ResourceNotFoundError(AppException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} with ID {resource_id} not found",
            status_code=404,
        )


class ValidationError(AppException):
    """Validation error."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            details=details,
            status_code=400,
        )
