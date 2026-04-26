from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.exception_handlers import domain_exception_handler, unhandled_exception_handler
from app.api.routers import auth, users
from app.core.config.settings import get_settings
from app.core.logging.logger import configure_logging
from app.core.middleware.correlation_id import CorrelationIdMiddleware
from app.domain.exceptions import DomainException

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

app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
