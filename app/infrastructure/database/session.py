"""Database session management."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.logging import logger


class DatabaseSessionManager:
    """Async database session manager (Singleton)."""

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self):
        """Initialize the async engine and session factory."""
        if self._engine is not None:
            logger.warning("Database engine already initialized.")
            return

        logger.info(f"Initializing database engine: {settings.DATABASE_URL.split('@')[-1]}")

        self._engine = create_async_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=True,
            echo=settings.DB_ECHO,
            future=True,
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        logger.info("Database session factory created.")

    async def close(self):
        """Close database connections."""
        if self._engine:
            logger.info("Closing database engine...")
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database engine closed.")

    def get_session_factory(self) -> async_sessionmaker:
        """Get the session factory."""
        if self._session_factory is None:
            raise RuntimeError("Database session manager not initialized.")
        return self._session_factory

    @property
    def engine(self):
        """Get the engine."""
        if self._engine is None:
            raise RuntimeError("Database session manager not initialized.")
        return self._engine


# Global instance
db_manager = DatabaseSessionManager()


# Dependency for FastAPI
async def get_db() -> AsyncSession:
    """FastAPI dependency to get a database session."""
    session_factory = db_manager.get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
