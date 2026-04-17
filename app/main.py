from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config.settings import get_settings
from app.core.logging.logger import configure_logging
from app.core.middleware.correlation_id import CorrelationIdMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(log_level=settings.LOG_LEVEL)
    yield


app = FastAPI(
    title="ServiceHub API",
    description="Multi-service booking platform",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(CorrelationIdMiddleware)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
