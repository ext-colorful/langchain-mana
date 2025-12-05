"""Basic tests for the application."""

import pytest


def test_import():
    """Test that core modules can be imported."""
    from app.core.config import settings
    from app.core.logging import logger

    assert settings is not None
    assert logger is not None


def test_constants():
    """Test constants."""
    from app.core.constants import MealAIStatus, ProviderType

    assert MealAIStatus.NORMAL == 0
    assert ProviderType.OPENAI == "openai"


def test_entities():
    """Test domain entities."""
    from app.domain.entities.food import Ingredient, FoodInfo

    ing = Ingredient(name="牛肉", quantity=100.0, unit="克")
    assert ing.name == "牛肉"

    food = FoodInfo(food_name="牛肉面", description="一碗牛肉面", ingredients=[ing])
    assert len(food.ingredients) == 1
