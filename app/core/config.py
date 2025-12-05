"""Configuration management using Pydantic Settings."""

import os
from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    # === Application ===
    APP_NAME: str = Field(default="Food Recognition System", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: Literal["development", "production"] = Field(
        default="development", description="Runtime environment"
    )
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )

    # === API Configuration ===
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=5513, description="API port")
    API_PREFIX: str = Field(default="/api/v1", description="API prefix")
    CORS_ORIGINS: list[str] = Field(default=["*"], description="CORS allowed origins")

    # === Database (PostgreSQL) ===
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/food_system",
        description="PostgreSQL connection URL (asyncpg for async support)",
    )
    DB_POOL_SIZE: int = Field(default=20, ge=1, le=100, description="Database pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50, description="Max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, ge=5, le=120, description="Pool timeout seconds")
    DB_POOL_RECYCLE: int = Field(default=3600, ge=600, le=7200, description="Pool recycle seconds")
    DB_ECHO: bool = Field(default=False, description="Echo SQL statements")

    # === Vector Store (ChromaDB) ===
    CHROMA_PERSIST_DIRECTORY: str = Field(
        default="./data/chroma", description="ChromaDB persist directory"
    )
    CHROMA_COLLECTION_INGREDIENTS: str = Field(
        default="ingredients", description="Ingredients collection name"
    )
    CHROMA_COLLECTION_MEALS: str = Field(default="meals", description="Meals collection name")
    CHROMA_DISTANCE_FUNCTION: Literal["l2", "ip", "cosine"] = Field(
        default="cosine", description="Distance metric"
    )

    # === Embedding Model ===
    EMBEDDING_MODEL_NAME: str = Field(
        default="text2vec-base-chinese", description="Text embedding model"
    )
    EMBEDDING_MODEL_PATH: Optional[str] = Field(
        default=None, description="Local model path (if not using HuggingFace)"
    )
    EMBEDDING_DIMENSION: int = Field(default=768, ge=128, le=4096, description="Embedding dimension")
    EMBEDDING_DEVICE: Literal["cpu", "cuda", "mps"] = Field(
        default="cpu", description="Device for embedding"
    )

    # === AI Model Configuration ===
    DEFAULT_LLM_PROVIDER: Literal["openai", "zhipu"] = Field(
        default="openai", description="Default LLM provider"
    )
    MODEL_NAME: str = Field(default="gpt-4", description="Default model name")
    MODEL_TEMPERATURE: float = Field(default=0.0, ge=0.0, le=2.0, description="Model temperature")
    MODEL_MAX_TOKENS: int = Field(default=2048, ge=128, le=32768, description="Max output tokens")

    # === OpenAI ===
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    OPENAI_API_BASE: str = Field(
        default="https://api.openai.com/v1", description="OpenAI base URL"
    )
    OPENAI_MODEL_NAME: str = Field(default="gpt-4", description="OpenAI model")

    # === Zhipu AI ===
    ZHIPU_API_KEY: Optional[str] = Field(default=None, description="Zhipu AI API key")
    ZHIPU_MODEL_NAME: str = Field(default="glm-4-plus", description="Zhipu model")
    ZHIPU_VISION_MODEL_NAME: str = Field(
        default="glm-4v-plus", description="Zhipu vision model"
    )

    # === RAG Configuration ===
    RAG_TOP_K: int = Field(default=5, ge=1, le=20, description="Top K results for RAG")
    RAG_SCORE_THRESHOLD: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Relevance score threshold"
    )
    RAG_USE_COMPRESSION: bool = Field(default=True, description="Use contextual compression")

    # === Task Configuration ===
    TASK_BATCH_SIZE: int = Field(default=1000, ge=100, le=5000, description="Batch size for tasks")
    TASK_SYNC_INTERVAL_SECONDS: int = Field(
        default=60, ge=10, le=3600, description="Task sync interval"
    )

    # === File Upload ===
    UPLOAD_DIR: str = Field(default="./data/uploads", description="File upload directory")
    UPLOAD_MAX_SIZE_MB: int = Field(default=10, ge=1, le=100, description="Max upload size in MB")
    UPLOAD_ALLOWED_EXTENSIONS: list[str] = Field(
        default=[".pdf", ".docx", ".txt", ".md", ".jpg", ".png"], description="Allowed file types"
    )

    # === Agent Runtime ===
    AGENT_MAX_ITERATIONS: int = Field(
        default=15, ge=1, le=50, description="Max agent iterations"
    )
    AGENT_TIMEOUT_SECONDS: int = Field(
        default=300, ge=30, le=1800, description="Agent timeout in seconds"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def adjust_log_level_for_production(cls, v: str, info) -> str:
        """Auto-adjust log level in production."""
        if info.data.get("ENVIRONMENT") == "production" and v == "DEBUG":
            return "WARNING"
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience access
settings = get_settings()
