"""AI食物识别智能体使用示例.

演示如何使用食物识别智能体进行文本和图片识别.
"""

import asyncio
import os
from dotenv import load_dotenv

from agent.graph import graph

# 加载环境变量
load_dotenv()


async def example_text_recognition():
    """示例：文本食物识别."""
    print("=" * 50)
    print("示例1: 文本食物识别")
    print("=" * 50)

    # 准备输入状态
    initial_state = {
        "description": "今天中午吃了一碗牛肉面，还有两个鸡蛋",
    }

    # 准备运行时上下文（可选，如果不提供则从环境变量读取）
    context = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "zhipu_api_key": os.getenv("ZHIPU_API_KEY"),
        "model_name": os.getenv("MODEL_NAME", "openai"),
    }

    # 调用图
    result = await graph.ainvoke(initial_state, config={"context": context})

    # 打印结果
    print("\n识别结果:")
    if result.get("error"):
        print(f"错误: {result['error']}")
    else:
        if result.get("food_info"):
            food_info = result["food_info"]
            print(f"菜品名称: {food_info.food_name}")
            print(f"描述: {food_info.description}")
            print("食材列表:")
            for ing in food_info.ingredients:
                print(f"  - {ing.name}: {ing.quantity} {ing.unit}")

        if result.get("nutritional_info"):
            print("\n营养成分分析:")
            for ing in result["nutritional_info"].ingredients:
                print(f"\n{ing.name} ({ing.quantity} {ing.unit}):")
                print(f"  卡路里: {ing.calories} 千卡")
                print(f"  蛋白质: {ing.protein} 克")
                print(f"  脂肪: {ing.fat} 克")
                print(f"  碳水化合物: {ing.carbohydrates} 克")


async def example_image_recognition():
    """示例：图片食物识别."""
    print("\n" + "=" * 50)
    print("示例2: 图片食物识别")
    print("=" * 50)

    # 准备输入状态（使用图片URL）
    initial_state = {
        "image_url": "https://example.com/food.jpg",  # 替换为实际的图片URL
    }

    # 准备运行时上下文
    context = {
        "zhipu_api_key": os.getenv("ZHIPU_API_KEY"),  # 图片识别必须使用智谱AI
    }

    # 调用图
    result = await graph.ainvoke(initial_state, config={"context": context})

    # 打印结果
    print("\n识别结果:")
    if result.get("error"):
        print(f"错误: {result['error']}")
    else:
        if result.get("food_info"):
            food_info = result["food_info"]
            print(f"菜品名称: {food_info.food_name}")
            print(f"描述: {food_info.description}")
            print("食材列表:")
            for ing in food_info.ingredients:
                print(f"  - {ing.name}: {ing.quantity} {ing.unit}")

        if result.get("nutritional_info"):
            print("\n营养成分分析:")
            for ing in result["nutritional_info"].ingredients:
                print(f"\n{ing.name} ({ing.quantity} {ing.unit}):")
                print(f"  卡路里: {ing.calories} 千卡")
                print(f"  蛋白质: {ing.protein} 克")
                print(f"  脂肪: {ing.fat} 克")
                print(f"  碳水化合物: {ing.carbohydrates} 克")


async def main():
    """主函数."""
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ZHIPU_API_KEY"):
        print("错误: 请设置 OPENAI_API_KEY 或 ZHIPU_API_KEY 环境变量")
        print("图片识别必须设置 ZHIPU_API_KEY")
        return

    # 运行文本识别示例
    await example_text_recognition()

    # 运行图片识别示例（需要有效的图片URL）
    # await example_image_recognition()


if __name__ == "__main__":
    asyncio.run(main())


