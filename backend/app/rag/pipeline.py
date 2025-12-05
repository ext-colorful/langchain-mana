"""RAG Pipeline - Document ingestion and retrieval
"""
from pathlib import Path
from typing import Any, Dict, List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from ..core.config import settings
from ..storage.chroma_db import chroma_manager
from ..utils.logger import get_logger
from .parsers.text_parser import DocxParser, HTMLParser, PDFParser, TextParser

logger = get_logger(__name__)


class ParserRegistry:
    """Registry for document parsers"""
    
    def __init__(self):
        self._parsers = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Register default parsers"""
        for parser_class in [TextParser, PDFParser, DocxParser, HTMLParser]:
            parser = parser_class()
            for ext in parser.supported_extensions:
                self._parsers[ext] = parser
    
    def get_parser(self, file_extension: str):
        """Get parser for file extension"""
        return self._parsers.get(file_extension.lower())
    
    def register_parser(self, parser):
        """Register a custom parser"""
        for ext in parser.supported_extensions:
            self._parsers[ext] = parser


class RAGPipeline:
    """RAG Pipeline for document ingestion and retrieval
    
    Pipeline steps:
    1. Parse document
    2. Split into chunks
    3. Generate embeddings
    4. Store in vector database
    """
    
    def __init__(self):
        self.parser_registry = ParserRegistry()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
    
    async def ingest_file(
        self,
        file_path: str,
        namespace: str,
        metadata: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Ingest a file into the knowledge base
        
        Args:
            file_path: Path to the file
            namespace: Knowledge base namespace
            metadata: Additional metadata
            
        Returns:
            Ingestion result with stats
        """
        try:
            # Step 1: Parse document
            file_ext = Path(file_path).suffix
            parser = self.parser_registry.get_parser(file_ext)
            
            if not parser:
                raise ValueError(f"No parser available for file type: {file_ext}")
            
            logger.info(f"Parsing file: {file_path}")
            documents = await parser.parse(file_path, metadata)
            
            # Step 2: Split into chunks
            logger.info(f"Splitting {len(documents)} documents into chunks")
            chunks = self.text_splitter.split_documents(documents)
            
            # Step 3: Add to vector store
            logger.info(f"Adding {len(chunks)} chunks to namespace: {namespace}")
            chunk_ids = chroma_manager.add_documents(namespace, chunks)
            
            return {
                "success": True,
                "file_path": file_path,
                "namespace": namespace,
                "total_documents": len(documents),
                "total_chunks": len(chunks),
                "chunk_ids": chunk_ids
            }
        
        except Exception as e:
            logger.error(f"Failed to ingest file {file_path}: {e}")
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e)
            }
    
    async def ingest_text(
        self,
        text: str,
        namespace: str,
        metadata: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Ingest raw text into knowledge base
        
        Args:
            text: Text content
            namespace: Knowledge base namespace
            metadata: Additional metadata
            
        Returns:
            Ingestion result
        """
        try:
            # Create document
            doc = Document(page_content=text, metadata=metadata or {})
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Add to vector store
            chunk_ids = chroma_manager.add_documents(namespace, chunks)
            
            return {
                "success": True,
                "total_chunks": len(chunks),
                "chunk_ids": chunk_ids
            }
        
        except Exception as e:
            logger.error(f"Failed to ingest text: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def retrieve(
        self,
        query: str,
        namespaces: List[str],
        k: int = None,
        score_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents from knowledge bases
        
        Args:
            query: Query text
            namespaces: List of knowledge base namespaces to search
            k: Number of results per namespace
            score_threshold: Minimum similarity score
            
        Returns:
            List of retrieval results
        """
        k = k or settings.TOP_K_RETRIEVAL
        score_threshold = score_threshold or settings.SIMILARITY_THRESHOLD
        
        all_results = []
        
        for namespace in namespaces:
            try:
                results = chroma_manager.search(
                    namespace=namespace,
                    query=query,
                    k=k,
                    score_threshold=score_threshold
                )
                
                for doc, score in results:
                    all_results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity_score": float(score),
                        "source": doc.metadata.get("source", namespace),
                        "namespace": namespace
                    })
            
            except Exception as e:
                logger.error(f"Failed to search namespace {namespace}: {e}")
                continue
        
        # Sort by score
        all_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return all_results[:k]
    
    def build_context(self, retrieval_results: List[Dict[str, Any]]) -> str:
        """Build context string from retrieval results
        
        Args:
            retrieval_results: List of retrieval results
            
        Returns:
            Formatted context string
        """
        if not retrieval_results:
            return ""
        
        context_parts = ["Here is relevant information from the knowledge base:\n"]
        
        for i, result in enumerate(retrieval_results, 1):
            context_parts.append(f"\n[Source {i}]")
            context_parts.append(f"Content: {result['content']}")
            context_parts.append(f"Source: {result['source']}")
            context_parts.append(f"Relevance: {result['similarity_score']:.2f}\n")
        
        return "\n".join(context_parts)


# Global RAG pipeline instance
rag_pipeline = RAGPipeline()
