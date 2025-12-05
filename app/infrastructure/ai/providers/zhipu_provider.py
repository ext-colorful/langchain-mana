"""Zhipu AI provider implementation."""

from __future__ import annotations

from typing import Any, AsyncIterator

from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import BaseMessage, HumanMessage

from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import logger
from app.infrastructure.ai.providers.base import BaseLLMProvider, VisionProviderMixin


class ZhipuProvider(BaseLLMProvider, VisionProviderMixin):
    """Zhipu AI provider with vision support."""

    name = "zhipu"
    supports_streaming = True

    def __init__(self):
        if not settings.ZHIPU_API_KEY:
            raise AIProviderError("ZHIPU_API_KEY not configured", provider=self.name)

        self.client = ChatZhipuAI(
            api_key=settings.ZHIPU_API_KEY,
            model=settings.ZHIPU_MODEL_NAME,
            temperature=settings.MODEL_TEMPERATURE,
        )

        self.vision_client = ChatZhipuAI(
            api_key=settings.ZHIPU_API_KEY,
            model=settings.ZHIPU_VISION_MODEL_NAME,
            temperature=settings.MODEL_TEMPERATURE,
        )

    async def ainvoke(self, messages: list[BaseMessage], **kwargs) -> Any:
        logger.debug(f"ZhipuProvider invoking model {settings.ZHIPU_MODEL_NAME}")
        response = await self.client.ainvoke(messages, **kwargs)
        return response

    async def astream(self, messages: list[BaseMessage], **kwargs) -> AsyncIterator[str]:
        logger.debug("ZhipuProvider streaming response")
        async for chunk in self.client.astream(messages, **kwargs):
            if chunk.content:
                yield chunk.content

    async def ainvoke_vision(self, prompt: str, image_url: str, **kwargs) -> Any:
        logger.info(f"ZhipuProvider invoking vision model with image: {image_url[:50]}...")
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        )
        response = await self.vision_client.ainvoke([message], **kwargs)
        return response
