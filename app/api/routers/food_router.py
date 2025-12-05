"""Food recognition router."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.services import get_food_recognition_service
from app.api.schemas.food_schemas import (
    FoodRecognitionRequest,
    FoodRecognitionResponse,
    IngredientResponse,
    MealResponse,
)
from app.application.services.food_recognition_service import FoodRecognitionService
from app.core.logging import logger

router = APIRouter(prefix="/food", tags=["food"])


@router.post("/ai", response_model=FoodRecognitionResponse)
async def food_ai_recognition(
    request: FoodRecognitionRequest,
    service: FoodRecognitionService = Depends(get_food_recognition_service),
):
    """AI food recognition endpoint."""
    if not request.description and not request.image_url:
        raise HTTPException(status_code=400, detail="Must provide description or image_url")

    logger.info(f"Processing food recognition for user: {request.user_id}")

    try:
        if request.description:
            meal = await service.recognize_from_text(
                user_id=request.user_id,
                description=request.description,
                timestamp=request.timestamp,
            )
        else:
            meal = await service.recognize_from_image(
                user_id=request.user_id,
                image_url=request.image_url,
                timestamp=request.timestamp,
            )

        return FoodRecognitionResponse(
            status="success",
            meal=MealResponse(
                id=meal.meal_id,
                user_id=meal.user_id,
                description=meal.description,
                date_time=meal.date_time.isoformat(),
            ),
            ingredients=[
                IngredientResponse(name=ing.name, quantity=ing.quantity, unit=ing.unit)
                for ing in meal.ingredients or []
            ],
        )

    except Exception as e:
        logger.exception("Error processing food recognition")
        raise HTTPException(status_code=500, detail=str(e))
