"""Provider registry for dynamic routing."""

from __future__ import annotations

from typing import Dict

from app.core.logging import logger
from app.infrastructure.ai.providers.base import BaseLLMProvider


class ProviderRegistry:
    """Registry for provider instances."""

    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}

    def register(self, provider: BaseLLMProvider) -> None:
        logger.info(f"Registering provider: {provider.name}")
        self._providers[provider.name] = provider

    def get(self, name: str) -> BaseLLMProvider:
        if name not in self._providers:
            raise KeyError(f"Provider not registered: {name}")
        return self._providers[name]

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())
