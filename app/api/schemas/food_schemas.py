"""Schemas for food endpoints."""

from pydantic import BaseModel, Field


class FoodRecognitionRequest(BaseModel):
    user_id: str = Field(..., description="User UUID")
    timestamp: int = Field(..., description="Unix timestamp")
    description: str | None = Field(None, description="Text description")
    image_url: str | None = Field(None, description="Image URL")


class IngredientResponse(BaseModel):
    name: str
    quantity: float
    unit: str


class MealResponse(BaseModel):
    id: int
    user_id: str
    description: str
    date_time: str


class FoodRecognitionResponse(BaseModel):
    status: str
    meal: MealResponse
    ingredients: list[IngredientResponse]
