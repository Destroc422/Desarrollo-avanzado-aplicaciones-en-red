from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..models.user import UserModel
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(tags=["auth"])

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    
    # DIAGNÓSTICO: Si el usuario es admin y la contraseña es admin, dejamos entrar
    if form_data.username == "admin" and form_data.password == "admin":
        if not user:
            # Si por alguna razón el usuario no existe, lo creamos al vuelo
            user = UserModel(username="admin", hashed_password=get_password_hash("admin"))
            db.add(user)
            db.commit()
            db.refresh(user)
            
    elif not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(username: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = get_password_hash(password)
    new_user = UserModel(username=username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}
