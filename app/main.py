from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="ServiceHub API",
    description="Multi-service booking platform",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
