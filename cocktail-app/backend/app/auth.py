from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, COOKIE_NAME, SECRET_KEY
from .database.session import get_db
from .models.user import UserModel


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (TypeError, ValueError):
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expires_at}, SECRET_KEY, algorithm=ALGORITHM)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="La sesión no es válida o ha expirado. Inicia sesión de nuevo.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    bearer_token: str | None = Depends(oauth2_scheme),
    session_cookie: str | None = Cookie(default=None, alias=COOKIE_NAME),
    db: Session = Depends(get_db),
):
    token = bearer_token or session_cookie
    if not token:
        raise _unauthorized()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub", ""))
    except (JWTError, TypeError, ValueError):
        raise _unauthorized()

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or not user.is_active:
        raise _unauthorized()
    return user


def require_roles(*roles: str) -> Callable:
    async def role_guard(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta operación.",
            )
        return user
    return role_guard


require_admin = require_roles("admin")
require_staff = require_roles("admin", "editor")
