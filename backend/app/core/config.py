"""Core configuration module for AI Agent Platform
"""
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Agent Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database - PostgreSQL
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="agent_platform")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # ChromaDB
    CHROMA_HOST: str = Field(default="localhost")
    CHROMA_PORT: int = 8001
    CHROMA_PERSIST_DIR: str = Field(default="./data/chroma")
    
    # File Storage
    STORAGE_TYPE: str = "local"  # local or minio
    STORAGE_PATH: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # MinIO (optional)
    MINIO_ENDPOINT: str | None = None
    MINIO_ACCESS_KEY: str | None = None
    MINIO_SECRET_KEY: str | None = None
    MINIO_BUCKET: str = "agent-platform"
    
    # Model Providers - OpenAI
    OPENAI_API_KEY: str | None = Field(default=None)
    OPENAI_BASE_URL: str | None = None
    OPENAI_DEFAULT_MODEL: str = "gpt-3.5-turbo"
    
    # Model Providers - DeepSeek
    DEEPSEEK_API_KEY: str | None = Field(default=None)
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_DEFAULT_MODEL: str = "deepseek-chat"
    
    # Model Providers - Qwen
    QWEN_API_KEY: str | None = Field(default=None)
    QWEN_BASE_URL: str | None = None
    QWEN_DEFAULT_MODEL: str = "qwen-turbo"
    
    # Model Providers - Anthropic
    ANTHROPIC_API_KEY: str | None = Field(default=None)
    ANTHROPIC_DEFAULT_MODEL: str = "claude-3-sonnet-20240229"
    
    # Embedding
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_PROVIDER: str = "openai"  # openai or local
    EMBEDDING_DIMENSION: int = 1536
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Agent Runtime
    MAX_ITERATIONS: int = 10
    AGENT_TIMEOUT: int = 300  # seconds
    MAX_CONCURRENT_AGENTS: int = 10
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"
    
    # Redis (optional, for task queue)
    REDIS_HOST: str | None = None
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Model Provider Configuration
class ModelProviderConfig:
    """Configuration for each model provider"""
    
    PROVIDERS = {
        "openai": {
            "api_key": settings.OPENAI_API_KEY,
            "base_url": settings.OPENAI_BASE_URL,
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "default": settings.OPENAI_DEFAULT_MODEL
        },
        "deepseek": {
            "api_key": settings.DEEPSEEK_API_KEY,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "models": ["deepseek-chat", "deepseek-coder"],
            "default": settings.DEEPSEEK_DEFAULT_MODEL
        },
        "qwen": {
            "api_key": settings.QWEN_API_KEY,
            "base_url": settings.QWEN_BASE_URL,
            "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
            "default": settings.QWEN_DEFAULT_MODEL
        },
        "anthropic": {
            "api_key": settings.ANTHROPIC_API_KEY,
            "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "default": settings.ANTHROPIC_DEFAULT_MODEL
        }
    }
    
    @classmethod
    def get_provider_config(cls, provider: str) -> dict:
        """Get configuration for a specific provider"""
        return cls.PROVIDERS.get(provider, {})
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of providers with valid API keys"""
        return [
            provider 
            for provider, config in cls.PROVIDERS.items() 
            if config.get("api_key")
        ]
