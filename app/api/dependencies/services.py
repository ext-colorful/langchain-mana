"""FastAPI dependencies for services."""

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.food_recognition_service import FoodRecognitionService
from app.application.services.model_router_service import ModelRouterService
from app.application.services.rag_service import RAGService
from app.infrastructure.database.repositories.meal_repository_impl import MealRepositoryImpl
from app.infrastructure.database.session import get_db


def get_model_router(request: Request) -> ModelRouterService:
    router: ModelRouterService = getattr(request.app.state, "model_router_service")
    return router


def get_rag_service(request: Request) -> RAGService:
    rag_service: RAGService = getattr(request.app.state, "rag_service")
    return rag_service


def get_food_recognition_service(
    db: AsyncSession = Depends(get_db),
    model_router: ModelRouterService = Depends(get_model_router),
    rag_service: RAGService = Depends(get_rag_service),
) -> FoodRecognitionService:
    meal_repo = MealRepositoryImpl(db)
    return FoodRecognitionService(meal_repo, model_router, rag_service)
