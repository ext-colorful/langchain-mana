"""File upload and ingestion router."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Request

from app.api.schemas.file_schemas import FileUploadResponse
from app.application.services.file_service import FileService
from app.application.services.rag_service import RAGService
from app.core.config import settings
from app.core.constants import Namespace
from app.core.logging import logger

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    namespace: str = Namespace.INGREDIENTS,
    request: Request = None,
):
    """Upload and ingest a file into RAG pipeline."""
    logger.info(f"Uploading file: {file.filename}")

    try:
        file_service = FileService()
        rag_service: RAGService = request.app.state.rag_service

        # Save file
        file_path = await file_service.save_file(file)

        # Parse file
        text, metadata = file_service.parse_file(file_path)
        metadata["filename"] = file.filename

        # Chunk text
        chunks = rag_service.chunk_text(text, metadata=metadata)

        # Ingest into vector store
        ids = await rag_service.ingest_documents(chunks, namespace=namespace)

        logger.info(f"File ingested: {len(chunks)} chunks created")

        return FileUploadResponse(
            filename=file.filename,
            metadata=metadata,
            chunks_ingested=len(chunks),
        )

    except Exception as exc:
        logger.exception("File upload error")
        raise HTTPException(status_code=500, detail=str(exc))
