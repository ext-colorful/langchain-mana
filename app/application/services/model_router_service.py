"""Model router service for multi-provider support."""

from __future__ import annotations

from typing import Optional

from app.core.config import settings
from app.core.constants import ProviderType
from app.core.exceptions import AIProviderError
from app.core.logging import logger
from app.infrastructure.ai.providers import BaseLLMProvider
from app.infrastructure.ai.providers.openai_provider import OpenAIProvider
from app.infrastructure.ai.providers.provider_registry import ProviderRegistry
from app.infrastructure.ai.providers.zhipu_provider import ZhipuProvider


class ModelRouterService:
    """Dynamic model router."""

    def __init__(self):
        self.registry = ProviderRegistry()
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        from app.infrastructure.ai.providers.mock_provider import MockProvider

        for provider_cls in (OpenAIProvider, ZhipuProvider):
            try:
                provider = provider_cls()
                self.registry.register(provider)
            except AIProviderError as exc:
                logger.warning(f"Provider disabled: {exc}")

        if not self.registry.list_providers():
            logger.warning("No real providers available. Falling back to MockProvider.")
            self.registry.register(MockProvider())

    def get_provider(self, name: str) -> BaseLLMProvider:
        return self.registry.get(name)

    def route(self, task_type: str, preferred_provider: Optional[str] = None) -> BaseLLMProvider:
        """Route to the appropriate provider based on task type."""
        provider_name = preferred_provider

        if not provider_name:
            if task_type == "vision":
                provider_name = ProviderType.ZHIPU
            else:
                provider_name = settings.DEFAULT_LLM_PROVIDER

        try:
            return self.registry.get(provider_name)
        except KeyError:
            available = self.registry.list_providers()
            if not available:
                raise AIProviderError("No providers available")
            logger.warning(
                f"Preferred provider '{provider_name}' unavailable. Falling back to '{available[0]}'."
            )
            return self.registry.get(available[0])
