"""Text file parsers (TXT, Markdown, etc.)
"""
from typing import List

from langchain_core.documents import Document

from .base import BaseParser


class TextParser(BaseParser):
    """Parser for plain text files"""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".txt", ".md", ".markdown"]
    
    async def parse(self, file_path: str, metadata: dict = None) -> List[Document]:
        """Parse text file"""
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        doc_metadata = metadata or {}
        doc_metadata["source"] = file_path
        
        return [Document(page_content=content, metadata=doc_metadata)]


class PDFParser(BaseParser):
    """Parser for PDF files"""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".pdf"]
    
    async def parse(self, file_path: str, metadata: dict = None) -> List[Document]:
        """Parse PDF file"""
        try:
            from langchain_community.document_loaders import PyPDFLoader
            
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Update metadata
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            return documents
        except ImportError:
            raise ImportError("PyPDF2 not installed. Run: pip install pypdf")


class DocxParser(BaseParser):
    """Parser for Word documents"""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".docx", ".doc"]
    
    async def parse(self, file_path: str, metadata: dict = None) -> List[Document]:
        """Parse Word document"""
        try:
            from langchain_community.document_loaders import Docx2txtLoader
            
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            return documents
        except ImportError:
            raise ImportError("docx2txt not installed. Run: pip install docx2txt")


class HTMLParser(BaseParser):
    """Parser for HTML files"""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".html", ".htm"]
    
    async def parse(self, file_path: str, metadata: dict = None) -> List[Document]:
        """Parse HTML file"""
        try:
            from langchain_community.document_loaders import UnstructuredHTMLLoader
            
            loader = UnstructuredHTMLLoader(file_path)
            documents = loader.load()
            
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            return documents
        except ImportError:
            raise ImportError("unstructured not installed. Run: pip install unstructured")
