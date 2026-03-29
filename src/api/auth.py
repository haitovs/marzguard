from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.config import Settings, get_settings

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    settings: Settings = Depends(get_settings),
):
    """Authenticate and return a JWT token."""
    if (
        form_data.username != settings.admin_username
        or not _verify_password(form_data.password, settings.admin_password, settings)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    token_data = {"sub": form_data.username, "exp": expire}
    access_token = jwt.encode(
        token_data, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    return Token(access_token=access_token)


def _verify_password(plain: str, stored: str, settings: Settings) -> bool:
    """Verify password. Supports both plain text (for initial setup) and bcrypt."""
    if stored.startswith("$2"):
        return pwd_context.verify(plain, stored)
    return plain == stored
