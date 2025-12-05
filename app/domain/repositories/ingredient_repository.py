"""Ingredient repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from app.domain.entities.food import Ingredient


class IngredientRepository(ABC):
    """Interface for ingredient persistence."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Ingredient]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, ingredient: Ingredient) -> Ingredient:
        raise NotImplementedError

    @abstractmethod
    async def bulk_create(self, ingredients: list[Ingredient]) -> list[Ingredient]:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, batch_size: int, offset: int) -> Iterable[Ingredient]:
        raise NotImplementedError

    @abstractmethod
    async def count_total(self) -> int:
        raise NotImplementedError
