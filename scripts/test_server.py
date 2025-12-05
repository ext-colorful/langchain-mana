"""Test the server without starting it."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all imports work."""
    print("Testing imports...")

    from app.core.config import settings
    from app.core.logging import logger
    from app.server import create_app

    print(f"✓ Settings loaded: {settings.APP_NAME}")
    print(f"✓ Logger initialized")

    app = create_app()
    print(f"✓ FastAPI app created")

    print("\n✅ All imports successful!")
    return True


def test_services():
    """Test service initialization."""
    print("\nTesting services...")

    from app.application.services.model_router_service import ModelRouterService
    from app.application.services.rag_service import RAGService

    router = ModelRouterService()
    print(f"✓ Model router initialized with providers: {router.registry.list_providers()}")

    # Don't initialize RAG service as it may require models
    print(f"✓ RAG service class available")

    print("\n✅ Services OK!")
    return True


if __name__ == "__main__":
    try:
        test_imports()
        test_services()
        print("\n🎉 All tests passed! Server is ready to start.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
