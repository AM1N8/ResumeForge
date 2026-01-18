"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.exceptions import AppException
from app.api.routes import health_router, github_router, resume_router
from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.core.logging import setup_logging, get_logger
from app.schemas.api_schemas import ErrorResponse, ErrorDetail

# Setup logging
setup_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler."""
    logger.info("application_starting")
    await init_db()
    logger.info("database_initialized")
    yield
    logger.info("application_shutting_down")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="AI Resume Structuring Agent",
    description="Transform unstructured resume data and GitHub profiles into clean, canonical resumes optimized for internship applications.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracing."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    logger.info(
        "request_started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    response = await call_next(request)

    logger.info(
        "request_completed",
        request_id=request_id,
        status_code=response.status_code,
    )

    response.headers["X-Request-ID"] = request_id
    return response


# Global exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions."""
    request_id = getattr(request.state, "request_id", None)

    logger.error(
        "application_error",
        code=exc.code,
        message=exc.message,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                details=exc.details,
                request_id=request_id,
            )
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, "request_id", None)

    logger.exception(
        "unexpected_error",
        error=str(exc),
        request_id=request_id,
    )

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                details=str(exc) if settings.debug else None,
                request_id=request_id,
            )
        ).model_dump(),
    )


# Register routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(resume_router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(github_router, prefix="/api/v1/github", tags=["GitHub"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Resume Structuring Agent API",
        "version": "0.1.0",
        "docs": "/docs",
    }
