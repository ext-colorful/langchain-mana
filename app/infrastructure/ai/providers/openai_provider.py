"""OpenAI provider implementation."""

from __future__ import annotations

from typing import Any, AsyncIterator

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import logger
from app.infrastructure.ai.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Chat provider."""

    name = "openai"
    supports_streaming = True

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise AIProviderError("OPENAI_API_KEY not configured", provider=self.name)
        self.model_name = settings.OPENAI_MODEL_NAME
        self.temperature = settings.MODEL_TEMPERATURE
        self.max_tokens = settings.MODEL_MAX_TOKENS
        self.client: BaseChatModel = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=self.temperature,
            model=self.model_name,
            max_tokens=self.max_tokens,
            streaming=True,
        )

    async def ainvoke(self, messages: list[BaseMessage], **kwargs) -> Any:
        logger.debug(f"OpenAIProvider invoking model {self.model_name}")
        response = await self.client.ainvoke(messages, **kwargs)
        return response

    async def astream(self, messages: list[BaseMessage], **kwargs) -> AsyncIterator[str]:
        logger.debug("OpenAIProvider streaming response")
        async for chunk in self.client.astream(messages, **kwargs):
            if chunk.content:
                yield chunk.content
