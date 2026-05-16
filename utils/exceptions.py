"""Custom exceptions for HomeService."""
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional


class HomeServiceException(HTTPException):
    """Base exception for HomeService."""

    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.headers = headers


class ResourceNotFoundException(HomeServiceException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str = "resource", identifier: Optional[str] = None):
        detail = f"{resource} not found" if not identifier else f"{resource} '{identifier}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvalidInputException(HomeServiceException):
    """Raised when input validation fails."""

    def __init__(self, field: str = "field", detail: str = "Invalid input"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field}: {detail}"
        )


class AuthenticationException(HomeServiceException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationException(HomeServiceException):
    """Raised when authorization fails."""

    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class DatabaseException(HomeServiceException):
    """Raised when database operations fail."""

    def __init__(self, detail: str = "Database error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class ExternalServiceException(HomeServiceException):
    """Raised when external service calls fail."""

    def __init__(
        self,
        service: str = "external service",
        detail: str = "Service unavailable",
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
    ):
        super().__init__(
            status_code=status_code,
            detail=f"{service} error: {detail}",
        )
