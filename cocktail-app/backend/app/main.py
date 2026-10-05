from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database.session import engine, Base
from .routes import cocktails, auth, uploads
from .exceptions import global_exception_handler
from fastapi import Request
from .auth import get_password_hash
from .models.user import UserModel
import os

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Estanco El Grillo - Cocktail API")

app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear usuario administrador por defecto si no existe
from .database.session import SessionLocal
db = SessionLocal()
user = db.query(UserModel).filter(UserModel.username == "admin").first()
if not user:
    admin_user = UserModel(
        username="admin", 
        hashed_password=get_password_hash("admin"), 
        role="admin"
    )
    db.add(admin_user)
    db.commit()
db.close()

# Servir archivos estáticos (imágenes subidas)
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(cocktails.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Estanco El Grillo API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
