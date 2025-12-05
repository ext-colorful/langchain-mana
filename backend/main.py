"""
AI Agent Platform - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import api_router
from app.tools import register_builtin_tools
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Agent Platform...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Register built-in tools
    register_builtin_tools()
    logger.info("Built-in tools registered")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Agent Platform...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade AI Agent Platform with multi-model support, RAG, and tool integration",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.storage.chroma_db import chroma_manager
    from app.models.router import model_router
    
    health = {
        "status": "healthy",
        "database": "ok",
        "chroma": "ok",
        "models": []
    }
    
    try:
        # Check ChromaDB
        chroma_manager.list_collections()
    except Exception as e:
        health["chroma"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    try:
        # Check available models
        available_models = model_router.list_available_models()
        health["models"] = list(available_models.keys())
    except Exception as e:
        health["models"] = f"error: {str(e)}"
    
    return health


@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring"""
    # TODO: Implement comprehensive metrics
    return {
        "total_requests": 0,
        "active_sessions": 0,
        "model_calls": 0,
        "tool_calls": 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS
    )
