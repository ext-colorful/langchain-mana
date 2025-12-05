"""SQLAlchemy models for meals and ingredients."""

from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class MealModel(Base):
    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    detail: Mapped[str | None] = mapped_column(Text)
    ai_status: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    pic_url: Mapped[list[str] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    ingredients: Mapped[List["MealIngredientModel"]] = relationship(
        "MealIngredientModel", back_populates="meal", cascade="all, delete-orphan"
    )


class FoodIngredientModel(Base):
    __tablename__ = "food_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    calories: Mapped[float | None] = mapped_column(Float)
    protein: Mapped[float | None] = mapped_column(Float)
    fat: Mapped[float | None] = mapped_column(Float)
    carbohydrates: Mapped[float | None] = mapped_column(Float)
    quantity: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(32))
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    meals: Mapped[List["MealIngredientModel"]] = relationship(
        "MealIngredientModel", back_populates="ingredient"
    )


class MealIngredientModel(Base):
    __tablename__ = "meal_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("food_ingredients.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(32))

    meal: Mapped[MealModel] = relationship("MealModel", back_populates="ingredients")
    ingredient: Mapped[FoodIngredientModel] = relationship(
        "FoodIngredientModel", back_populates="meals"
    )


class AiMealRecognitionModel(Base):
    __tablename__ = "ai_meal_recognitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str | None] = mapped_column(Text)
    pic_url: Mapped[str | None] = mapped_column(String(512))
    ai_chat_message_id: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    meal: Mapped[MealModel] = relationship("MealModel")
