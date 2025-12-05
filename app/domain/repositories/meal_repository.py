"""Meal repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, Optional

from app.domain.entities.food import Meal


class MealRepository(ABC):
    """Interface for meal persistence."""

    @abstractmethod
    async def create_meal(self, meal: Meal) -> Meal:
        raise NotImplementedError

    @abstractmethod
    async def update_status(self, meal_id: int, ai_status: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_meals_for_sync(self, batch_size: int) -> Iterable[Meal]:
        raise NotImplementedError

    @abstractmethod
    async def get_meal(self, meal_id: int) -> Optional[Meal]:
        raise NotImplementedError

    @abstractmethod
    async def get_total_meals(self) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_synced_meals(self) -> int:
        raise NotImplementedError
