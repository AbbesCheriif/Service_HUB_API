from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config.settings import get_settings
from app.domain.exceptions import InvalidCredentials

_settings = get_settings()


class JWTService:
    def create_access_token(self, subject: str, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return self._encode({"sub": subject, "role": role, "type": "access", "exp": expire})

    def create_refresh_token(self, subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=_settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return self._encode({"sub": subject, "type": "refresh", "exp": expire})

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, _settings.SECRET_KEY, algorithms=[_settings.ALGORITHM])
        except JWTError:
            raise InvalidCredentials()

    def _encode(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload, _settings.SECRET_KEY, algorithm=_settings.ALGORITHM)
