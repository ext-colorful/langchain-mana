"""Pydantic schemas for Knowledge Base operations
"""
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class FileStatus(str, Enum):
    """File processing status"""
    UPLOADING = "uploading"
    PARSING = "parsing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class KnowledgeBaseCreate(BaseModel):
    """Schema for creating a knowledge base"""
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    embedding_model: str | None = Field(default="text-embedding-3-small")
    chunk_size: int = Field(default=1000, ge=100, le=4000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)


class KnowledgeBaseUpdate(BaseModel):
    """Schema for updating a knowledge base"""
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    chunk_size: int | None = Field(None, ge=100, le=4000)
    chunk_overlap: int | None = Field(None, ge=0, le=1000)


class KnowledgeBaseResponse(BaseModel):
    """Schema for knowledge base response"""
    id: int
    user_id: int
    name: str
    description: str | None
    namespace: str
    embedding_model: str | None
    chunk_size: int
    chunk_overlap: int
    created_at: datetime
    updated_at: datetime | None
    
    # Stats
    total_files: int = 0
    total_chunks: int = 0
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    file_id: int
    filename: str
    file_type: str
    file_size: int
    status: FileStatus
    message: str = "File uploaded successfully"


class FileResponse(BaseModel):
    """Schema for file response"""
    id: int
    knowledge_base_id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: FileStatus
    error_message: str | None
    total_chunks: int
    processed_chunks: int
    created_at: datetime
    updated_at: datetime | None
    
    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Schema for file list response"""
    total: int
    files: List[FileResponse]


class QueryRequest(BaseModel):
    """Schema for querying knowledge base"""
    query: str = Field(..., min_length=1)
    knowledge_base_ids: List[int] | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class RetrievalResult(BaseModel):
    """Schema for a single retrieval result"""
    content: str
    metadata: dict
    similarity_score: float
    source: str


class QueryResponse(BaseModel):
    """Schema for query response"""
    query: str
    results: List[RetrievalResult]
    total_results: int
