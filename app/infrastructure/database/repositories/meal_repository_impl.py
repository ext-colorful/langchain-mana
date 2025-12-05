"""Meal repository implementation."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MealAIStatus
from app.domain.entities.food import Ingredient, Meal
from app.domain.repositories.meal_repository import MealRepository
from app.infrastructure.database.models.food_models import (
    FoodIngredientModel,
    MealIngredientModel,
    MealModel,
)


class MealRepositoryImpl(MealRepository):
    """PostgreSQL implementation of MealRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_meal(self, meal: Meal) -> Meal:
        """Create a meal with ingredients."""
        db_meal = MealModel(
            user_id=meal.user_id,
            description=meal.description,
            date_time=meal.date_time,
            ai_status=meal.ai_status,
            pic_url=meal.pic_url or [],
            detail=meal.detail,
        )

        self.session.add(db_meal)
        await self.session.flush()

        # Associate ingredients
        if meal.ingredients:
            for ing in meal.ingredients:
                # Find or create ingredient
                stmt = select(FoodIngredientModel).where(FoodIngredientModel.name == ing.name)
                result = await self.session.execute(stmt)
                db_ing = result.scalar_one_or_none()

                if not db_ing:
                    db_ing = FoodIngredientModel(
                        name=ing.name,
                        calories=ing.calories,
                        protein=ing.protein,
                        fat=ing.fat,
                        carbohydrates=ing.carbohydrates,
                        quantity=ing.quantity,
                        unit=ing.unit,
                    )
                    self.session.add(db_ing)
                    await self.session.flush()

                # Create meal-ingredient relationship
                meal_ing = MealIngredientModel(
                    meal_id=db_meal.id, ingredient_id=db_ing.id, quantity=ing.quantity, unit=ing.unit
                )
                self.session.add(meal_ing)

        await self.session.commit()
        meal.meal_id = db_meal.id
        return meal

    async def update_status(self, meal_id: int, ai_status: int) -> None:
        """Update meal AI status."""
        stmt = (
            update(MealModel)
            .where(MealModel.id == meal_id)
            .values(ai_status=ai_status, updated_at=datetime.utcnow())
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def list_meals_for_sync(self, batch_size: int) -> Iterable[Meal]:
        """List meals that match sync conditions."""
        stmt = (
            select(MealModel)
            .where(
                MealModel.description != "",
                MealModel.ai_status.in_([MealAIStatus.NORMAL, MealAIStatus.CONFIRMED]),
            )
            .limit(batch_size)
        )
        result = await self.session.execute(stmt)
        db_meals = result.scalars().all()

        return [
            Meal(
                meal_id=m.id,
                user_id=m.user_id,
                description=m.description,
                date_time=m.date_time,
                ai_status=m.ai_status,
                pic_url=m.pic_url,
                detail=m.detail,
            )
            for m in db_meals
        ]

    async def get_meal(self, meal_id: int) -> Optional[Meal]:
        """Get a meal by ID."""
        stmt = select(MealModel).where(MealModel.id == meal_id)
        result = await self.session.execute(stmt)
        db_meal = result.scalar_one_or_none()

        if not db_meal:
            return None

        return Meal(
            meal_id=db_meal.id,
            user_id=db_meal.user_id,
            description=db_meal.description,
            date_time=db_meal.date_time,
            ai_status=db_meal.ai_status,
            pic_url=db_meal.pic_url,
            detail=db_meal.detail,
        )

    async def get_total_meals(self) -> int:
        """Get total meal count."""
        stmt = select(func.count(MealModel.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_synced_meals(self) -> int:
        """Get synced meal count."""
        # Placeholder - In real scenario, track sync status separately
        return 0
