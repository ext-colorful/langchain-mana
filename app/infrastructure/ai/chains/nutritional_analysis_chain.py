"""Nutritional analysis chain using RAG."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.logging import logger
from app.domain.entities.food import Ingredient, NutritionalInfo
from app.infrastructure.ai.providers.base import BaseLLMProvider
from app.infrastructure.vector_store.chroma.manager import ChromaVectorStore


NUTRITION_SYSTEM_PROMPT = """你是一位营养分析专家。根据菜品和食材列表，结合检索到的营养数据库信息，
返回每个食材的营养成分（卡路里、蛋白质、脂肪、碳水化合物）。
考虑烹饪方式对营养的影响。

返回 JSON 格式：
{"ingredients": [{"name": "...", "quantity": 100, "unit": "克", "calories": 150.0, "protein": 20.0, "fat": 5.0, "carbohydrates": 30.0}]}

仅返回 JSON，无其他文字。"""


class NutritionalAnalysisChain:
    """Chain for nutritional analysis using RAG."""

    def __init__(self, provider: BaseLLMProvider, vector_store: ChromaVectorStore):
        self.provider = provider
        self.vector_store = vector_store

    async def analyze(self, food_name: str, ingredients: list[Ingredient]) -> NutritionalInfo:
        """Analyze nutrition using RAG."""
        # Retrieve similar ingredients from vector store
        query = food_name + " " + " ".join([i.name for i in ingredients])
        retrieval_results = await self.vector_store.similarity_search(query, k=5)

        context = "\n".join([f"食材: {doc.page_content}" for doc in retrieval_results[:3]])

        user_message = f"""菜品名称: {food_name}
食材列表: {[ing.name for ing in ingredients]}

检索到的营养参考:
{context}

请分析每个食材的营养成分。"""

        messages = [SystemMessage(content=NUTRITION_SYSTEM_PROMPT), HumanMessage(content=user_message)]

        response = await self.provider.ainvoke(messages)
        content = response.content.strip()

        logger.debug(f"Nutritional analysis response: {content}")

        try:
            # Clean JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)
            analyzed_ingredients = [
                Ingredient(
                    name=ing["name"],
                    quantity=float(ing.get("quantity", 0)),
                    unit=ing.get("unit", "克"),
                    calories=float(ing.get("calories", 0)),
                    protein=float(ing.get("protein", 0)),
                    fat=float(ing.get("fat", 0)),
                    carbohydrates=float(ing.get("carbohydrates", 0)),
                )
                for ing in data["ingredients"]
            ]
            return NutritionalInfo(ingredients=analyzed_ingredients)
        except Exception as exc:
            logger.error(f"Failed to parse nutrition analysis: {exc}")
            # Return original ingredients with default values
            return NutritionalInfo(
                ingredients=[
                    Ingredient(
                        name=ing.name,
                        quantity=ing.quantity,
                        unit=ing.unit,
                        calories=0.0,
                        protein=0.0,
                        fat=0.0,
                        carbohydrates=0.0,
                    )
                    for ing in ingredients
                ]
            )
