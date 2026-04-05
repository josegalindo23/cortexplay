"""
CortexPlay - FastAPI Application Entry Point

Main application module that initializes the FastAPI app,
configures CORS middleware, and registers all API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import brain, clips

from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="CortexPlay API",
    description=(
        "Backend API for CortexPlay — an interactive 3D brain visualizer "
        "powered by TRIBE v2 fMRI predictions (d'Ascoli et al., 2026, Meta FAIR)."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount("/videos", StaticFiles(directory="./data/videos"), name="videos")

# CORS Middleware
# Allows the React frontend (localhost:5173) to communicate with the API

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers

app.include_router(brain.router, prefix="/api/brain", tags=["Brain"])
app.include_router(clips.router, prefix="/api/clips", tags=["Clips"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "project": "CortexPlay",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check for monitoring."""
    return {
        "status": "healthy",
        "model": "TRIBE v2",
        "paper": "d'Ascoli et al., 2026, Meta FAIR",
    }