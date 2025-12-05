"""Application constants."""

class TaskStatus:
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    PUSHED = 4


class MealAIStatus:
    NORMAL = 0
    PROCESSING = 1
    COMPLETED_PENDING = 2
    CONFIRMED = 3


class AIMealTaskStatus:
    NOT_STARTED = 0
    RUNNING = 1
    FINISHED = 2
    FAILED = 3
    PUSHED = 4


class ProviderType:
    OPENAI = "openai"
    ZHIPU = "zhipu"


class Namespace:
    INGREDIENTS = "ingredients"
    MEALS = "meals"
