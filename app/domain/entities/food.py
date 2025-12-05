"""Food-related domain entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Ingredient:
    """Ingredient entity with nutritional info."""

    name: str
    quantity: float
    unit: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbohydrates: Optional[float] = None
    id: Optional[int] = None


@dataclass
class FoodInfo:
    """Extracted food information."""

    food_name: str
    description: str
    ingredients: list[Ingredient]


@dataclass
class NutritionalInfo:
    """Nutritional analysis result."""

    ingredients: list[Ingredient]

    @property
    def total_calories(self) -> float:
        return sum(i.calories or 0 for i in self.ingredients)

    @property
    def total_protein(self) -> float:
        return sum(i.protein or 0 for i in self.ingredients)

    @property
    def total_fat(self) -> float:
        return sum(i.fat or 0 for i in self.ingredients)

    @property
    def total_carbohydrates(self) -> float:
        return sum(i.carbohydrates or 0 for i in self.ingredients)


@dataclass
class Meal:
    """Meal entity."""

    user_id: str
    description: str
    date_time: datetime
    ai_status: int
    meal_id: Optional[int] = None
    pic_url: Optional[list[str]] = None
    detail: Optional[str] = None
    ingredients: Optional[list[Ingredient]] = None
