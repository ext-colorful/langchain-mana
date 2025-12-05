"""Custom application exceptions."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ConfigurationError(AppException):
    """Configuration error."""

    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")


class DatabaseError(AppException):
    """Database operation error."""

    def __init__(self, message: str):
        super().__init__(message, "DB_ERROR")


class VectorStoreError(AppException):
    """Vector store operation error."""

    def __init__(self, message: str):
        super().__init__(message, "VECTOR_STORE_ERROR")


class AIProviderError(AppException):
    """AI model provider error."""

    def __init__(self, message: str, provider: str = "unknown"):
        self.provider = provider
        super().__init__(f"[{provider}] {message}", "AI_PROVIDER_ERROR")


class ValidationError(AppException):
    """Data validation error."""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class ResourceNotFoundError(AppException):
    """Resource not found error."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} not found: {identifier}", "NOT_FOUND")


class PermissionDeniedError(AppException):
    """Permission denied error."""

    def __init__(self, message: str):
        super().__init__(message, "PERMISSION_DENIED")


class FileProcessingError(AppException):
    """File processing error."""

    def __init__(self, message: str):
        super().__init__(message, "FILE_PROCESSING_ERROR")


class AgentRuntimeError(AppException):
    """Agent runtime error."""

    def __init__(self, message: str):
        super().__init__(message, "AGENT_RUNTIME_ERROR")
