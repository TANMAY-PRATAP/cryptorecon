"""CryptoRecon V4.0 - Main FastAPI Application with Forensic Dashboard."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.api.v1.api_router import api_v1_router
from app.core.bloom_filter import get_bloom_filter
from app.storage.redis_client import get_redis_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cryptorecon")

FRONTEND_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown routines."""
    settings = get_settings()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.APP_ENV}]...")
    
    # 1. Initialize In-Memory Bloom Filter & Entity Store
    bloom = get_bloom_filter()
    logger.info(
        f"In-Memory Bloom Filter initialized: {bloom.total_entities} verified entities indexed "
        f"({bloom.memory_usage_bytes / 1024:.2f} KB bitarray)."
    )

    # 2. Initialize Redis connection
    redis_mgr = get_redis_manager()
    await redis_mgr.connect()

    yield

    # Shutdown
    logger.info("Shutting down CryptoRecon engine...")
    await redis_mgr.disconnect()
    logger.info("Shutdown complete.")


def create_application() -> FastAPI:
    """Factory function for FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=f"{settings.PROJECT_NAME} (V4.0 Master Architecture)",
        description=(
            "Multi-Chain Forensic Reconnaissance, VASP Attribution & Autonomous Asset Recovery Engine "
            "for Cyber Crime Cells (1930 / I4C / NCRP), State Police Units, and FIU-IND."
        ),
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global Exception Handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred during forensic execution.",
                "detail": str(exc) if settings.DEBUG else None
            }
        )

    # Mount API Routers
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    @app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
    async def dashboard():
        """Serve the interactive Next.js / Cytoscape.js Forensic Visualizer Dashboard."""
        if os.path.exists(FRONTEND_FILE):
            with open(FRONTEND_FILE, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>CryptoRecon Dashboard Frontend</h1>"

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "tagline": "Multi-Chain Forensic Reconnaissance & VASP Attribution Engine",
            "dashboard": "/dashboard",
            "docs": "/docs",
            "health": f"{settings.API_V1_STR}/health",
            "ingest_endpoint": f"{settings.API_V1_STR}/cases/ingest"
        }

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
