"""Chat processing router."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from app.api.schemas.chat_schemas import ChatProcessRequest, ChatProcessResponse
from app.application.services.chat_service import ChatService
from app.application.services.model_router_service import ModelRouterService
from app.core.logging import logger

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(request: Request) -> ChatService:
    model_router: ModelRouterService = request.app.state.model_router_service
    return ChatService(model_router)


@router.post("/process", response_model=ChatProcessResponse)
async def chat_process(
    req: ChatProcessRequest,
    service: ChatService = Depends(get_chat_service),
):
    """Synchronous chat processing."""
    logger.info(f"Processing chat request from user: {req.user_id}")
    try:
        result = await service.process(req.text, user_id=req.user_id, session_id=req.session_id)
        return result
    except Exception as exc:
        logger.exception("Chat processing error")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/process_stream")
async def chat_process_stream(
    req: ChatProcessRequest,
    service: ChatService = Depends(get_chat_service),
):
    """Streaming chat processing."""
    logger.info(f"Streaming chat request from user: {req.user_id}")

    async def generate():
        try:
            async for chunk in service.stream(req.text, user_id=req.user_id, session_id=req.session_id):
                yield {"data": chunk}
            yield {"data": "[DONE]"}
        except Exception as exc:
            logger.exception("Stream error")
            yield {"data": f"[ERROR] {exc}"}

    return EventSourceResponse(generate())
