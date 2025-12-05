"""Schemas for file upload."""

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    filename: str
    metadata: dict
    chunks_ingested: int
