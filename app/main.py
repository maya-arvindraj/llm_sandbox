from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes.chat import router as chat_router
from core.config import get_settings
from core.logging import configure_logging
from dependencies import (
    close_dependencies,
    init_dependencies,
)


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    """

    configure_logging()

    await init_dependencies()

    yield

    await close_dependencies()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


app.include_router(chat_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Basic application health check.
    """

    return {
        "status": "ok",
    }