from fastapi import FastAPI

from infrastructure.config.api_defaults import load_api_settings
from infrastructure.entrypoints.api.routers.analyze_email import router as analyze_email_router
from infrastructure.entrypoints.api.routers.health import router as health_router
from infrastructure.entrypoints.api.routers.model_assessment import (
    router as model_assessment_router,
)


def create_app() -> FastAPI:
    app = FastAPI(title="PhishShield")
    app.state.api_settings = load_api_settings()
    app.include_router(analyze_email_router)
    app.include_router(health_router)
    app.include_router(model_assessment_router)

    return app
