from fastapi import FastAPI

from infrastructure.entrypoints.api.routers.analyze_email import router as analyze_email_router


def create_app() -> FastAPI:
    app = FastAPI(title="PhishShield")
    app.include_router(analyze_email_router)

    return app
