"""Model Router - Dynamic model selection and routing
"""
from enum import Enum
from typing import Any, Dict, List

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from ..core.config import ModelProviderConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RoutingStrategy(str, Enum):
    """Model routing strategies"""
    COST = "cost"
    SPEED = "speed"
    QUALITY = "quality"
    FALLBACK = "fallback"


class ModelRouter:
    """Intelligent model router that selects appropriate model based on:
    - Cost optimization
    - Speed requirements
    - Quality requirements
    - Fallback strategies
    """
    
    def __init__(self):
        self._model_cache: Dict[str, BaseChatModel] = {}
        self._model_costs = self._load_model_costs()
        self._model_speeds = self._load_model_speeds()
        self._model_quality = self._load_model_quality()
    
    def _load_model_costs(self) -> Dict[str, float]:
        """Load model cost per 1M tokens (approximate)"""
        return {
            "gpt-4": 30.0,
            "gpt-4-turbo": 10.0,
            "gpt-3.5-turbo": 0.5,
            "deepseek-chat": 0.14,
            "deepseek-coder": 0.14,
            "qwen-turbo": 0.3,
            "qwen-plus": 0.8,
            "qwen-max": 2.0,
            "claude-3-opus-20240229": 15.0,
            "claude-3-sonnet-20240229": 3.0,
            "claude-3-haiku-20240307": 0.25,
        }
    
    def _load_model_speeds(self) -> Dict[str, int]:
        """Load model speed ranking (lower is faster)"""
        return {
            "gpt-3.5-turbo": 1,
            "claude-3-haiku-20240307": 2,
            "deepseek-chat": 3,
            "qwen-turbo": 4,
            "gpt-4-turbo": 5,
            "qwen-plus": 6,
            "claude-3-sonnet-20240229": 7,
            "qwen-max": 8,
            "deepseek-coder": 9,
            "gpt-4": 10,
            "claude-3-opus-20240229": 11,
        }
    
    def _load_model_quality(self) -> Dict[str, int]:
        """Load model quality ranking (higher is better)"""
        return {
            "gpt-4": 10,
            "claude-3-opus-20240229": 10,
            "gpt-4-turbo": 9,
            "claude-3-sonnet-20240229": 8,
            "qwen-max": 7,
            "deepseek-coder": 7,
            "qwen-plus": 6,
            "deepseek-chat": 5,
            "gpt-3.5-turbo": 5,
            "qwen-turbo": 4,
            "claude-3-haiku-20240307": 4,
        }
    
    def get_model(
        self,
        provider: str | None = None,
        model_name: str | None = None,
        strategy: RoutingStrategy = RoutingStrategy.COST,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> BaseChatModel:
        """Get appropriate model based on strategy
        
        Args:
            provider: Specific provider (openai, deepseek, qwen, anthropic)
            model_name: Specific model name
            strategy: Routing strategy
            temperature: Model temperature
            max_tokens: Max tokens for completion
            **kwargs: Additional model parameters
        
        Returns:
            BaseChatModel instance
        """
        # If specific model requested, use it
        if provider and model_name:
            cache_key = f"{provider}:{model_name}"
            if cache_key in self._model_cache:
                return self._model_cache[cache_key]
            
            model = self._create_model(provider, model_name, temperature, max_tokens, **kwargs)
            self._model_cache[cache_key] = model
            return model
        
        # Otherwise, select based on strategy
        selected_provider, selected_model = self._select_by_strategy(strategy, provider)
        
        cache_key = f"{selected_provider}:{selected_model}"
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]
        
        model = self._create_model(selected_provider, selected_model, temperature, max_tokens, **kwargs)
        self._model_cache[cache_key] = model
        
        logger.info(f"Model selected: {selected_provider}/{selected_model} (strategy: {strategy})")
        return model
    
    def _select_by_strategy(self, strategy: RoutingStrategy, preferred_provider: str | None = None) -> tuple:
        """Select model based on routing strategy"""
        available_providers = ModelProviderConfig.get_available_providers()
        
        if not available_providers:
            raise ValueError("No model providers configured. Please set API keys in environment.")
        
        # Filter by preferred provider if specified
        if preferred_provider and preferred_provider in available_providers:
            available_providers = [preferred_provider]
        
        if strategy == RoutingStrategy.COST:
            return self._select_by_cost(available_providers)
        elif strategy == RoutingStrategy.SPEED:
            return self._select_by_speed(available_providers)
        elif strategy == RoutingStrategy.QUALITY:
            return self._select_by_quality(available_providers)
        else:
            # Fallback to first available
            provider = available_providers[0]
            config = ModelProviderConfig.get_provider_config(provider)
            return provider, config["default"]
    
    def _select_by_cost(self, providers: List[str]) -> tuple:
        """Select cheapest available model"""
        best_cost = float('inf')
        best_provider = None
        best_model = None
        
        for provider in providers:
            config = ModelProviderConfig.get_provider_config(provider)
            for model in config.get("models", []):
                cost = self._model_costs.get(model, 999.0)
                if cost < best_cost:
                    best_cost = cost
                    best_provider = provider
                    best_model = model
        
        return best_provider, best_model
    
    def _select_by_speed(self, providers: List[str]) -> tuple:
        """Select fastest available model"""
        best_speed = float('inf')
        best_provider = None
        best_model = None
        
        for provider in providers:
            config = ModelProviderConfig.get_provider_config(provider)
            for model in config.get("models", []):
                speed = self._model_speeds.get(model, 999)
                if speed < best_speed:
                    best_speed = speed
                    best_provider = provider
                    best_model = model
        
        return best_provider, best_model
    
    def _select_by_quality(self, providers: List[str]) -> tuple:
        """Select highest quality available model"""
        best_quality = 0
        best_provider = None
        best_model = None
        
        for provider in providers:
            config = ModelProviderConfig.get_provider_config(provider)
            for model in config.get("models", []):
                quality = self._model_quality.get(model, 0)
                if quality > best_quality:
                    best_quality = quality
                    best_provider = provider
                    best_model = model
        
        return best_provider, best_model
    
    def _create_model(
        self,
        provider: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> BaseChatModel:
        """Create model instance based on provider"""
        config = ModelProviderConfig.get_provider_config(provider)
        
        if not config or not config.get("api_key"):
            raise ValueError(f"Provider {provider} not configured or missing API key")
        
        if provider == "openai":
            return ChatOpenAI(
                api_key=config["api_key"],
                base_url=config.get("base_url"),
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        elif provider == "deepseek":
            # DeepSeek uses OpenAI-compatible API
            return ChatOpenAI(
                api_key=config["api_key"],
                base_url=config["base_url"],
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        elif provider == "qwen":
            # Qwen uses OpenAI-compatible API
            return ChatOpenAI(
                api_key=config["api_key"],
                base_url=config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        elif provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    api_key=config["api_key"],
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            except ImportError:
                raise ImportError("langchain-anthropic not installed. Run: pip install langchain-anthropic")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """List all available models by provider"""
        result = {}
        for provider in ModelProviderConfig.get_available_providers():
            config = ModelProviderConfig.get_provider_config(provider)
            result[provider] = config.get("models", [])
        return result
    
    def get_model_info(self, provider: str, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model"""
        return {
            "provider": provider,
            "model": model_name,
            "cost_per_1m_tokens": self._model_costs.get(model_name, "Unknown"),
            "speed_rank": self._model_speeds.get(model_name, "Unknown"),
            "quality_rank": self._model_quality.get(model_name, "Unknown"),
        }


# Global router instance
model_router = ModelRouter()
