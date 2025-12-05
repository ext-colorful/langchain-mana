"""Embedding model factory."""

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

from app.core.config import settings
from app.core.logging import logger


def create_embedding_model() -> Embeddings:
    """Create embedding model instance."""
    logger.info(f"Creating embedding model: {settings.EMBEDDING_MODEL_NAME}")

    model_kwargs = {"device": settings.EMBEDDING_DEVICE}
    encode_kwargs = {"normalize_embeddings": True}

    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL_PATH or settings.EMBEDDING_MODEL_NAME,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )

    logger.info("Embedding model created successfully.")
    return embeddings
