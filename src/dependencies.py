from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.core.tracker import IPTracker
from src.models.database import get_session_factory

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Global singletons set during app startup
_tracker: IPTracker | None = None


def set_tracker(tracker: IPTracker):
    global _tracker
    _tracker = tracker


def get_tracker() -> IPTracker:
    if _tracker is None:
        raise RuntimeError("Tracker not initialized")
    return _tracker


async def get_db() -> AsyncSession:
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def get_current_admin(
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    """Validate JWT token and return the admin username."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
            timezone.utc
        ):
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
