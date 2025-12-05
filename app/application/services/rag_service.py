"""RAG pipeline service."""

from __future__ import annotations

import asyncio
import os
from typing import Iterable, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from app.core.config import settings
from app.core.logging import logger
from app.infrastructure.vector_store.chroma.manager import ChromaManager, ChromaVectorStore
from app.infrastructure.vector_store.embeddings.embedding_factory import create_embedding_model


class RAGService:
    """Handles chunking, embeddings, and vector store operations."""

    def __init__(self):
        self.embedding = create_embedding_model()
        self.chroma_manager = ChromaManager(self.embedding)
        self.chunker = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)

    def get_collection(self, namespace: str) -> ChromaVectorStore:
        return self.chroma_manager.get_collection(namespace)

    async def ingest_documents(
        self,
        documents: Iterable[Document],
        namespace: str,
        metadatas: Optional[list[dict]] = None,
    ) -> list[str]:
        """Ingest documents into vector store."""
        texts = [doc.page_content for doc in documents]
        metadatas = metadatas or [doc.metadata for doc in documents]
        collection = self.get_collection(namespace)
        return await collection.add_texts(texts=texts, metadatas=metadatas)

    def chunk_text(self, text: str, metadata: Optional[dict] = None) -> list[Document]:
        """Chunk raw text into LangChain documents."""
        docs = self.chunker.create_documents([text], metadatas=[metadata or {}])
        return docs

    async def query(self, query: str, namespace: str, k: int = 5):
        collection = self.get_collection(namespace)
        return await collection.similarity_search(query, k=k)

    async def similarity_search_with_score(self, query: str, namespace: str, k: int = 5):
        collection = self.get_collection(namespace)
        return await collection.similarity_search_with_score(query, k=k)
