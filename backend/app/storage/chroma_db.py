"""ChromaDB vector store integration
"""
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from ..core.config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ChromaDBManager:
    """ChromaDB manager for vector storage
    Supports multiple namespaces (collections) for knowledge base isolation
    """
    
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIR
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embeddings
        self.embeddings = self._init_embeddings()
        
        logger.info(f"ChromaDB initialized at: {self.persist_directory}")
    
    def _init_embeddings(self):
        """Initialize embedding model"""
        if settings.EMBEDDING_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set for embeddings")
            return OpenAIEmbeddings(
                api_key=settings.OPENAI_API_KEY,
                model=settings.EMBEDDING_MODEL
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {settings.EMBEDDING_PROVIDER}")
    
    def create_collection(self, namespace: str) -> Chroma:
        """Create or get a collection (knowledge base)
        
        Args:
            namespace: Unique namespace for the collection
            
        Returns:
            Chroma vectorstore instance
        """
        try:
            vectorstore = Chroma(
                collection_name=namespace,
                embedding_function=self.embeddings,
                client=self.client,
                persist_directory=self.persist_directory
            )
            logger.info(f"Collection created/loaded: {namespace}")
            return vectorstore
        except Exception as e:
            logger.error(f"Failed to create collection {namespace}: {e}")
            raise
    
    def add_documents(
        self,
        namespace: str,
        documents: List[Document],
        metadata: Dict[str, Any] | None = None
    ) -> List[str]:
        """Add documents to a collection
        
        Args:
            namespace: Collection namespace
            documents: List of LangChain Document objects
            metadata: Additional metadata to attach to all documents
            
        Returns:
            List of document IDs
        """
        vectorstore = self.create_collection(namespace)
        
        # Add metadata to each document
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)
        
        ids = vectorstore.add_documents(documents)
        logger.info(f"Added {len(documents)} documents to {namespace}")
        return ids
    
    def search(
        self,
        namespace: str,
        query: str,
        k: int = 5,
        filter_dict: Dict[str, Any] | None = None,
        score_threshold: float | None = None
    ) -> List[tuple]:
        """Search documents in a collection
        
        Args:
            namespace: Collection namespace
            query: Query text
            k: Number of results to return
            filter_dict: Metadata filters
            score_threshold: Minimum similarity score
            
        Returns:
            List of (Document, score) tuples
        """
        vectorstore = self.create_collection(namespace)
        
        if score_threshold:
            results = vectorstore.similarity_search_with_relevance_scores(
                query,
                k=k,
                filter=filter_dict
            )
            results = [(doc, score) for doc, score in results if score >= score_threshold]
        else:
            docs = vectorstore.similarity_search(
                query,
                k=k,
                filter=filter_dict
            )
            results = [(doc, 1.0) for doc in docs]  # No score available
        
        logger.info(f"Search in {namespace} returned {len(results)} results")
        return results
    
    def delete_collection(self, namespace: str):
        """Delete a collection"""
        try:
            self.client.delete_collection(namespace)
            logger.info(f"Collection deleted: {namespace}")
        except Exception as e:
            logger.error(f"Failed to delete collection {namespace}: {e}")
            raise
    
    def delete_documents(self, namespace: str, ids: List[str]):
        """Delete specific documents from a collection"""
        collection = self.client.get_collection(namespace)
        collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents from {namespace}")
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        collections = self.client.list_collections()
        return [c.name for c in collections]
    
    def get_collection_count(self, namespace: str) -> int:
        """Get number of documents in a collection"""
        try:
            collection = self.client.get_collection(namespace)
            return collection.count()
        except Exception:
            return 0


# Global ChromaDB manager instance
chroma_manager = ChromaDBManager()
