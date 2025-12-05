"""Knowledge Base API endpoints
"""
import os
import uuid
from pathlib import Path
from typing import List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.database import get_db
from ...core.security import get_current_user
from ...rag.pipeline import rag_pipeline
from ...schemas.knowledge import (
    FileListResponse,
    FileResponse,
    FileUploadResponse,
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    QueryRequest,
    QueryResponse,
    RetrievalResult,
)
from ...storage.chroma_db import chroma_manager
from ...storage.models import File as FileModel
from ...storage.models import FileStatus, KnowledgeBase
from ...utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/create", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new knowledge base"""
    try:
        # Generate unique namespace
        namespace = f"kb_{uuid.uuid4().hex[:16]}"
        
        # Create knowledge base
        kb = KnowledgeBase(
            user_id=current_user["user_id"],
            name=kb_data.name,
            description=kb_data.description,
            namespace=namespace,
            embedding_model=kb_data.embedding_model,
            chunk_size=kb_data.chunk_size,
            chunk_overlap=kb_data.chunk_overlap
        )
        
        db.add(kb)
        await db.commit()
        await db.refresh(kb)
        
        # Create ChromaDB collection
        chroma_manager.create_collection(namespace)
        
        logger.info(f"Knowledge base created: {kb.id} with namespace {namespace}")
        
        response = KnowledgeBaseResponse.model_validate(kb)
        response.total_files = 0
        response.total_chunks = 0
        
        return response
    
    except Exception as e:
        logger.error(f"Failed to create knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's knowledge bases"""
    try:
        stmt = select(KnowledgeBase).where(
            KnowledgeBase.user_id == current_user["user_id"]
        )
        result = await db.execute(stmt)
        kbs = result.scalars().all()
        
        # Add stats
        response_kbs = []
        for kb in kbs:
            kb_response = KnowledgeBaseResponse.model_validate(kb)
            kb_response.total_files = len(kb.files)
            kb_response.total_chunks = chroma_manager.get_collection_count(kb.namespace)
            response_kbs.append(kb_response)
        
        return response_kbs
    
    except Exception as e:
        logger.error(f"Failed to list knowledge bases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_id}/upload", response_model=FileUploadResponse)
async def upload_file(
    kb_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload file to knowledge base"""
    try:
        # Get knowledge base
        stmt = select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user["user_id"]
        )
        result = await db.execute(stmt)
        kb = result.scalar_one_or_none()
        
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        # Validate file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Save file
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = Path(settings.STORAGE_PATH) / unique_filename
        
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Create file record
        file_record = FileModel(
            knowledge_base_id=kb.id,
            filename=unique_filename,
            original_filename=file.filename,
            file_type=file_ext.lstrip('.'),
            file_size=file_size,
            file_path=str(file_path),
            status=FileStatus.UPLOADING
        )
        
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)
        
        # Schedule background processing
        background_tasks.add_task(
            process_file_async,
            file_record.id,
            str(file_path),
            kb.namespace,
            kb.id
        )
        
        logger.info(f"File uploaded: {file_record.id} to KB {kb_id}")
        
        return FileUploadResponse(
            file_id=file_record.id,
            filename=unique_filename,
            file_type=file_ext.lstrip('.'),
            file_size=file_size,
            status=FileStatus.PARSING
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_file_async(file_id: int, file_path: str, namespace: str, kb_id: int):
    """Background task to process uploaded file"""
    from ...core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # Update status
            stmt = select(FileModel).where(FileModel.id == file_id)
            result = await db.execute(stmt)
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                return
            
            file_record.status = FileStatus.PROCESSING
            await db.commit()
            
            # Process file
            result = await rag_pipeline.ingest_file(
                file_path=file_path,
                namespace=namespace,
                metadata={
                    "file_id": file_id,
                    "kb_id": kb_id,
                    "filename": file_record.original_filename
                }
            )
            
            # Update status
            if result["success"]:
                file_record.status = FileStatus.COMPLETED
                file_record.total_chunks = result["total_chunks"]
                file_record.processed_chunks = result["total_chunks"]
            else:
                file_record.status = FileStatus.FAILED
                file_record.error_message = result.get("error", "Unknown error")
            
            await db.commit()
            logger.info(f"File processed: {file_id}, status: {file_record.status}")
        
        except Exception as e:
            logger.error(f"Failed to process file {file_id}: {e}")
            # Update status to failed
            file_record.status = FileStatus.FAILED
            file_record.error_message = str(e)
            await db.commit()


@router.get("/{kb_id}/files", response_model=FileListResponse)
async def list_files(
    kb_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List files in knowledge base"""
    try:
        # Verify ownership
        stmt = select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user["user_id"]
        )
        result = await db.execute(stmt)
        kb = result.scalar_one_or_none()
        
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        # Get files
        files = kb.files
        
        return FileListResponse(
            total=len(files),
            files=[FileResponse.model_validate(f) for f in files]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Query knowledge bases"""
    try:
        # Get knowledge bases
        kb_ids = request.knowledge_base_ids or []
        
        stmt = select(KnowledgeBase).where(
            KnowledgeBase.id.in_(kb_ids),
            KnowledgeBase.user_id == current_user["user_id"]
        )
        result = await db.execute(stmt)
        kbs = result.scalars().all()
        
        if not kbs:
            raise HTTPException(status_code=404, detail="No valid knowledge bases found")
        
        # Get namespaces
        namespaces = [kb.namespace for kb in kbs]
        
        # Retrieve
        results = rag_pipeline.retrieve(
            query=request.query,
            namespaces=namespaces,
            k=request.top_k,
            score_threshold=request.similarity_threshold
        )
        
        return QueryResponse(
            query=request.query,
            results=[RetrievalResult(**r) for r in results],
            total_results=len(results)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete knowledge base"""
    try:
        stmt = select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user["user_id"]
        )
        result = await db.execute(stmt)
        kb = result.scalar_one_or_none()
        
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        # Delete ChromaDB collection
        chroma_manager.delete_collection(kb.namespace)
        
        # Delete from database
        await db.delete(kb)
        await db.commit()
        
        logger.info(f"Knowledge base deleted: {kb_id}")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))
