"""Base classes for AI providers."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class BaseLLMProvider(ABC):
    """Abstract base provider."""

    name: str
    supports_streaming: bool = False

    @abstractmethod
    async def ainvoke(self, messages: list[Any], **kwargs) -> Any:
        raise NotImplementedError

    async def astream(self, messages: list[Any], **kwargs) -> AsyncIterator[str]:
        raise NotImplementedError


class VisionProviderMixin:
    """Mixin for providers that support vision inputs."""

    @abstractmethod
    async def ainvoke_vision(self, prompt: str, image_url: str, **kwargs) -> Any:
        raise NotImplementedError
