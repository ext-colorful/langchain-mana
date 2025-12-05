"""Image recognition chain using vision models."""

from __future__ import annotations

from langchain_core.messages import SystemMessage

from app.core.logging import logger
from app.domain.entities.food import FoodInfo, Ingredient
from app.infrastructure.ai.providers.base import BaseLLMProvider, VisionProviderMixin


VISION_PROMPT = """你是一个专业的食物视觉识别助手。
根据用户上传的食物图片，识别主要菜品，并输出 JSON：
{"food_name": "...", "description": "...", "ingredients": [{"name": "...", "quantity": 100, "unit": "克"}]}
请根据常识估算数量。
仅返回 JSON。"""


class ImageRecognitionChain:
    """Chain for image-based food recognition."""

    def __init__(self, provider: VisionProviderMixin):
        self.provider = provider

    async def recognize(self, image_url: str, prompt: str | None = None) -> FoodInfo:
        prompt = prompt or "请识别图片中的食物信息"

        response = await self.provider.ainvoke_vision(VISION_PROMPT + "\n" + prompt, image_url)
        content = response.content
        logger.debug(f"Vision response: {content}")

        try:
            import json

            data = json.loads(content)
            return FoodInfo(
                food_name=data.get("food_name", "未知菜品"),
                description=data.get("description", ""),
                ingredients=[
                    Ingredient(
                        name=ing.get("name", "未知食材"),
                        quantity=float(ing.get("quantity", 0)),
                        unit=ing.get("unit", "份"),
                    )
                    for ing in data.get("ingredients", [])
                ],
            )
        except Exception as exc:
            logger.error(f"Failed to parse vision result: {exc}")
            return FoodInfo(food_name="未知菜品", description="", ingredients=[])
