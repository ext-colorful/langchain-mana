"""Worker for background task processing."""

import asyncio

from app.core.logging import logger


class TaskWorker:
    """Simple task worker for async job processing."""

    def __init__(self):
        self.running = False
        self.task_queue: asyncio.Queue = asyncio.Queue()

    async def start(self):
        self.running = True
        logger.info("Task worker started")
        while self.running:
            try:
                task_func, args, kwargs = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                logger.info(f"Executing task: {task_func.__name__}")
                await task_func(*args, **kwargs)
                self.task_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                logger.error(f"Task execution error: {exc}")

    def stop(self):
        self.running = False
        logger.info("Task worker stopped")

    async def enqueue(self, task_func, *args, **kwargs):
        await self.task_queue.put((task_func, args, kwargs))
