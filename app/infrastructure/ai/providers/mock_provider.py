"""Mock provider for development and tests."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage

from app.infrastructure.ai.providers.base import BaseLLMProvider, VisionProviderMixin


class MockProvider(BaseLLMProvider, VisionProviderMixin):
    """A lightweight mock provider returning deterministic responses."""

    name = "mock"
    supports_streaming = True

    async def ainvoke(self, messages: list[BaseMessage], **kwargs) -> Any:
        last_message = messages[-1]
        content = last_message.content if isinstance(last_message.content, str) else str(last_message.content)
        payload = {
            "food_name": content[:10] or "未知",
            "description": content,
            "ingredients": [
                {"name": "牛肉", "quantity": 100, "unit": "克"},
                {"name": "面条", "quantity": 200, "unit": "克"},
            ],
        }
        return AIMessage(content=json.dumps(payload, ensure_ascii=False))

    async def astream(self, messages: list[BaseMessage], **kwargs) -> AsyncIterator[str]:
        response = await self.ainvoke(messages, **kwargs)
        text = response.content
        for chunk in [text[i : i + 20] for i in range(0, len(text), 20)]:
            yield chunk

    async def ainvoke_vision(self, prompt: str, image_url: str, **kwargs) -> Any:
        payload = {
            "food_name": "图像菜品",
            "description": f"来自图片: {image_url}",
            "ingredients": [
                {"name": "番茄", "quantity": 50, "unit": "克"},
                {"name": "鸡蛋", "quantity": 2, "unit": "个"},
            ],
        }
        return AIMessage(content=json.dumps(payload, ensure_ascii=False))
