"""Food extraction chain using LangChain."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.core.logging import logger
from app.domain.entities.food import FoodInfo, Ingredient
from app.infrastructure.ai.providers.base import BaseLLMProvider


FOOD_EXTRACTION_SYSTEM_PROMPT = """你是一个专业的食物识别助手。从用户的文本描述中提取食物信息。

请以 JSON 格式返回，包含：
- food_name: 菜品名称
- description: 详细描述
- ingredients: 食材列表，每个食材包含 name (名称), quantity (数量), unit (单位)

示例：
{"food_name": "牛肉面", "description": "一碗牛肉面", "ingredients": [{"name": "牛肉", "quantity": 100, "unit": "克"}, {"name": "面条", "quantity": 200, "unit": "克"}]}

仅返回 JSON，不要额外的文字。"""


class FoodExtractionChain:
    """Chain for extracting food information from text."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def extract(self, text: str) -> FoodInfo:
        """Extract food info from text."""
        messages = [
            SystemMessage(content=FOOD_EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=text),
        ]

        response = await self.provider.ainvoke(messages)
        content = response.content

        logger.debug(f"Raw LLM response: {content}")

        # Clean JSON response (remove comments and extra text)
        content = re.sub(r"//.*", "", content)  # remove comments
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            data = json.loads(content)
            return FoodInfo(
                food_name=data["food_name"],
                description=data["description"],
                ingredients=[
                    Ingredient(
                        name=ing["name"],
                        quantity=float(ing.get("quantity", 0)),
                        unit=ing.get("unit", "份"),
                    )
                    for ing in data.get("ingredients", [])
                ],
            )
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.error(f"Content: {content}")
            # Fallback
            return FoodInfo(food_name=text[:30], description=text, ingredients=[])
