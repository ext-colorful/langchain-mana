"""Base parser interface for document parsing
"""
from abc import ABC, abstractmethod
from typing import List

from langchain_core.documents import Document


class BaseParser(ABC):
    """Base class for all document parsers"""
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions"""
        pass
    
    @abstractmethod
    async def parse(self, file_path: str, metadata: dict = None) -> List[Document]:
        """Parse document and return LangChain Document objects
        
        Args:
            file_path: Path to the file
            metadata: Additional metadata to attach
            
        Returns:
            List of Document objects
        """
        pass
