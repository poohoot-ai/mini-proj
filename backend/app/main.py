"""FastAPI entry point for the group-order service."""

from fastapi import FastAPI

from backend.app.core.config import Settings, load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the API application with validated server-side settings."""

    resolved_settings = settings or load_settings()
    application = FastAPI(
        title="Group Order Agent API",
        version="0.1.0",
    )
    application.state.settings = resolved_settings

    @application.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {
            "status": "healthy",
            "environment": resolved_settings.app_env,
            "model": resolved_settings.openai_model,
        }

    return application


app = create_app()
