"""Chat processing service."""

from __future__ import annotations

from typing import AsyncIterator

from langchain_core.messages import HumanMessage, SystemMessage

from app.application.services.model_router_service import ModelRouterService
from app.application.services.session_service import SessionService
from app.core.logging import logger

DEFAULT_SYSTEM_PROMPT = "你是一个营养与饮食助手，帮助用户分析食物与营养信息。"


class ChatService:
    """Handles chat requests and streaming responses."""

    def __init__(self, model_router: ModelRouterService, session_service: SessionService | None = None):
        self.model_router = model_router
        self.session_service = session_service

    async def process(self, text: str, user_id: str | None = None, session_id: str | None = None):
        provider = self.model_router.route(task_type="text")

        messages = [SystemMessage(content=DEFAULT_SYSTEM_PROMPT), HumanMessage(content=text)]
        response = await provider.ainvoke(messages)
        logger.debug(f"LLM response: {response.content}")

        await self._record_message(session_id, role="assistant", content=response.content)

        return {
            "content": response.content,
            "model": provider.name,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    async def stream(
        self, text: str, user_id: str | None = None, session_id: str | None = None
    ) -> AsyncIterator[str]:
        provider = self.model_router.route(task_type="text")
        messages = [SystemMessage(content=DEFAULT_SYSTEM_PROMPT), HumanMessage(content=text)]

        async for chunk in provider.astream(messages):
            yield chunk

    async def _record_message(self, session_id: str | None, role: str, content: str) -> None:
        if not session_id or not self.session_service:
            return
        await self.session_service.append_message(session_id, role=role, content=content)
