from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, get_password_hash, verify_password
from ..core.config import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_NAME, COOKIE_SECURE, FRONTEND_URL
from ..database.session import get_db
from ..models.user import UserModel
from ..schemas.user import UserCreate, UserRead


router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, user: UserModel) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=create_access_token(user.id),
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/api/v1",
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserCreate,
    response: Response,
    db: Session = Depends(get_db),
):
    exists = db.query(UserModel).filter(
        or_(UserModel.username == payload.username, UserModel.email == payload.email)
    ).first()
    if exists:
        raise HTTPException(status_code=409, detail="Ese usuario o correo ya está registrado.")

    user = UserModel(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name.strip(),
        phone=payload.phone.strip(),
        national_id=payload.national_id.strip(),
        address=payload.address.strip(),
        city=payload.city.strip(),
        hashed_password=get_password_hash(payload.password),
        role="customer",
        is_active=True,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="No fue posible registrar la cuenta con esos datos.")
    _set_session_cookie(response, user)
    return user


@router.post("/token", response_model=UserRead)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not user.is_active or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    _set_session_cookie(response, user)
    return user


@router.get("/me", response_model=UserRead)
def read_current_user(user: UserModel = Depends(get_current_user)):
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/api/v1",
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    response.headers["Clear-Site-Data"] = '"cache"'
