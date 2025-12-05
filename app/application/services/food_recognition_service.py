"""Food recognition service orchestrator."""

from __future__ import annotations

from datetime import datetime

from app.core.constants import MealAIStatus, Namespace
from app.core.logging import logger
from app.domain.entities.food import Meal
from app.domain.repositories.meal_repository import MealRepository
from app.infrastructure.ai.chains.food_extraction_chain import FoodExtractionChain
from app.infrastructure.ai.chains.image_recognition_chain import ImageRecognitionChain
from app.infrastructure.ai.chains.nutritional_analysis_chain import NutritionalAnalysisChain
from app.infrastructure.ai.providers.base import VisionProviderMixin
from app.application.services.model_router_service import ModelRouterService
from app.application.services.rag_service import RAGService


class FoodRecognitionService:
    """Orchestrates food recognition workflow."""

    def __init__(
        self,
        meal_repo: MealRepository,
        model_router: ModelRouterService,
        rag_service: RAGService,
    ):
        self.meal_repo = meal_repo
        self.model_router = model_router
        self.rag_service = rag_service

    async def recognize_from_text(self, user_id: str, description: str, timestamp: int) -> Meal:
        """Recognize food from text description."""
        logger.info(f"Recognizing food from text for user: {user_id}")

        # 1. Extract food info
        provider = self.model_router.route(task_type="text")
        chain = FoodExtractionChain(provider)
        food_info = await chain.extract(description)

        logger.info(f"Extracted food: {food_info.food_name}, ingredients: {len(food_info.ingredients)}")

        # 2. Analyze nutrition using RAG
        vector_store = self.rag_service.get_collection(Namespace.INGREDIENTS)
        nutrition_chain = NutritionalAnalysisChain(provider, vector_store)
        nutrition_info = await nutrition_chain.analyze(food_info.food_name, food_info.ingredients)

        # 3. Save to database
        meal = Meal(
            user_id=user_id,
            description=food_info.description or description,
            date_time=datetime.fromtimestamp(timestamp),
            ai_status=MealAIStatus.COMPLETED_PENDING,
            detail=food_info.food_name,
            ingredients=nutrition_info.ingredients,
        )

        meal = await self.meal_repo.create_meal(meal)
        logger.info(f"Meal created with ID: {meal.meal_id}")

        return meal

    async def recognize_from_image(self, user_id: str, image_url: str, timestamp: int) -> Meal:
        """Recognize food from image URL."""
        logger.info(f"Recognizing food from image for user: {user_id}")

        # 1. Image recognition
        provider = self.model_router.route(task_type="vision")
        if not isinstance(provider, VisionProviderMixin):
            raise ValueError("Provider does not support vision")

        vision_chain = ImageRecognitionChain(provider)
        food_info = await vision_chain.recognize(image_url)

        logger.info(f"Recognized food: {food_info.food_name}")

        # 2. Analyze nutrition
        text_provider = self.model_router.route(task_type="text")
        vector_store = self.rag_service.get_collection(Namespace.INGREDIENTS)
        nutrition_chain = NutritionalAnalysisChain(text_provider, vector_store)
        nutrition_info = await nutrition_chain.analyze(food_info.food_name, food_info.ingredients)

        # 3. Save to database
        meal = Meal(
            user_id=user_id,
            description=food_info.description,
            date_time=datetime.fromtimestamp(timestamp),
            ai_status=MealAIStatus.COMPLETED_PENDING,
            pic_url=[image_url],
            detail=food_info.food_name,
            ingredients=nutrition_info.ingredients,
        )

        meal = await self.meal_repo.create_meal(meal)
        logger.info(f"Meal created with ID: {meal.meal_id}")

        return meal
