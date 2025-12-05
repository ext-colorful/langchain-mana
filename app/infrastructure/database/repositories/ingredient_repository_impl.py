"""Ingredient repository implementation."""

from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.food import Ingredient
from app.domain.repositories.ingredient_repository import IngredientRepository
from app.infrastructure.database.models.food_models import FoodIngredientModel


class IngredientRepositoryImpl(IngredientRepository):
    """SQLAlchemy implementation for ingredients."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Optional[Ingredient]:
        stmt = select(FoodIngredientModel).where(FoodIngredientModel.name == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def create(self, ingredient: Ingredient) -> Ingredient:
        model = FoodIngredientModel(
            name=ingredient.name,
            calories=ingredient.calories,
            protein=ingredient.protein,
            fat=ingredient.fat,
            carbohydrates=ingredient.carbohydrates,
            quantity=ingredient.quantity,
            unit=ingredient.unit,
        )
        self.session.add(model)
        await self.session.commit()
        ingredient.id = model.id
        return ingredient

    async def bulk_create(self, ingredients: list[Ingredient]) -> list[Ingredient]:
        models = [
            FoodIngredientModel(
                name=i.name,
                calories=i.calories,
                protein=i.protein,
                fat=i.fat,
                carbohydrates=i.carbohydrates,
                quantity=i.quantity,
                unit=i.unit,
            )
            for i in ingredients
        ]
        self.session.add_all(models)
        await self.session.commit()
        for ing, model in zip(ingredients, models, strict=False):
            ing.id = model.id
        return ingredients

    async def list_all(self, batch_size: int, offset: int) -> Iterable[Ingredient]:
        stmt = (
            select(FoodIngredientModel)
            .order_by(FoodIngredientModel.id)
            .offset(offset)
            .limit(batch_size)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count_total(self) -> int:
        stmt = select(FoodIngredientModel)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    @staticmethod
    def _to_entity(model: FoodIngredientModel) -> Ingredient:
        return Ingredient(
            id=model.id,
            name=model.name,
            calories=model.calories,
            protein=model.protein,
            fat=model.fat,
            carbohydrates=model.carbohydrates,
            quantity=model.quantity or 0,
            unit=model.unit or "g",
        )
