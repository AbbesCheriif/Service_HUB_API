from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    BookingConflict,
    BookingNotFound,
    DomainException,
    InvalidCredentials,
    PermissionDenied,
    ServiceNotFound,
    UserAlreadyExists,
    UserNotFound,
)

_STATUS_MAP: dict[type[DomainException], int] = {
    UserNotFound: 404,
    ServiceNotFound: 404,
    BookingNotFound: 404,
    UserAlreadyExists: 409,
    BookingConflict: 409,
    InvalidCredentials: 401,
    PermissionDenied: 403,
}


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    status_code = _STATUS_MAP.get(type(exc), 400)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
