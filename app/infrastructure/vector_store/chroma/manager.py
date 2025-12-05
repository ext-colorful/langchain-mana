"""Chroma vector store manager."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, Iterable, Optional

from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings

from app.core.config import settings
from app.core.logging import logger


class ChromaVectorStore:
    """Wrapper around LangChain Chroma vector store."""

    def __init__(self, collection_name: str, embedding: Embeddings, persist_directory: str):
        self.collection_name = collection_name
        self.embedding = embedding
        self.persist_directory = persist_directory
        self._store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding,
            persist_directory=persist_directory,
        )

    async def add_texts(
        self,
        texts: list[str],
        metadatas: Optional[list[dict[str, Any]]] = None,
        ids: Optional[list[str]] = None,
    ) -> list[str]:
        return await asyncio.to_thread(self._store.add_texts, texts, metadatas, ids)

    async def similarity_search(self, query: str, k: int = 5) -> list[Any]:
        return await asyncio.to_thread(self._store.similarity_search, query, k)

    async def similarity_search_with_score(self, query: str, k: int = 5) -> list[tuple[Any, float]]:
        return await asyncio.to_thread(self._store.similarity_search_with_score, query, k)

    async def delete(self, ids: list[str]) -> None:
        await asyncio.to_thread(self._store.delete, ids)

    def as_retriever(self, **kwargs):
        return self._store.as_retriever(**kwargs)


class ChromaManager:
    """Manage multiple Chroma vector stores by namespace."""

    def __init__(self, embedding: Embeddings):
        self.embedding = embedding
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_directory, exist_ok=True)
        self._collections: dict[str, ChromaVectorStore] = {}

    def get_collection(self, namespace: str) -> ChromaVectorStore:
        if namespace not in self._collections:
            logger.info(f"Creating Chroma collection: {namespace}")
            self._collections[namespace] = ChromaVectorStore(
                collection_name=namespace,
                embedding=self.embedding,
                persist_directory=self.persist_directory,
            )
        return self._collections[namespace]


_chroma_manager: Optional[ChromaManager] = None


def get_chroma_manager(embedding: Optional[Embeddings] = None) -> ChromaManager:
    global _chroma_manager
    if _chroma_manager is None:
        if embedding is None:
            raise RuntimeError("Embedding model must be provided for the first initialization")
        _chroma_manager = ChromaManager(embedding)
    return _chroma_manager
