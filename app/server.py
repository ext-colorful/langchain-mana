"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middlewares.logging_middleware import LoggingMiddleware
from app.api.routers import food_router, chat_router, file_router, sync_router
from app.application.services.model_router_service import ModelRouterService
from app.application.services.rag_service import RAGService
from app.core.config import settings
from app.core.logging import logger
from app.infrastructure.database.session import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("=" * 60)

    # Initialize database
    db_manager.initialize()
    logger.info("Database initialized")

    # Initialize global services
    app.state.model_router_service = ModelRouterService()
    logger.info("Model router initialized")

    app.state.rag_service = RAGService()
    logger.info("RAG service initialized")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await db_manager.close()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Enterprise Food Recognition & Nutrition Analysis System",
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    # Routers
    app.include_router(food_router.router, prefix=settings.API_PREFIX)
    app.include_router(chat_router.router, prefix=settings.API_PREFIX)
    app.include_router(file_router.router, prefix=settings.API_PREFIX)
    app.include_router(sync_router.router, prefix=settings.API_PREFIX)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.APP_VERSION}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
