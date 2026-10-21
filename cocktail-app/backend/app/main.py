from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.config import FRONTEND_ORIGINS, UPLOAD_DIR
from .database.migrations import upgrade_existing_sqlite_schema
from .database.session import Base, engine
from .exceptions import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from .models import CocktailModel, OrderModel, ServiceAddonModel, UserModel
from .routes import auth, business, cocktails, external_catalog, orders, service_addons, uploads


def create_app() -> FastAPI:
    # Importing models above registers the complete schema before create_all.
    Base.metadata.create_all(bind=engine)
    upgrade_existing_sqlite_schema(engine)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    application = FastAPI(
        title="Estanco y Coctelería El Grillo",
        version="1.0.0",
        description="API versionada para catálogo, clientes, pedidos y administración.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=FRONTEND_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Accept", "Authorization", "Content-Type"],
    )
    application.add_exception_handler(Exception, global_exception_handler)
    application.add_exception_handler(StarletteHTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)

    application.include_router(auth.router, prefix="/api/v1")
    application.include_router(cocktails.router, prefix="/api/v1")
    application.include_router(uploads.router, prefix="/api/v1")
    application.include_router(service_addons.router, prefix="/api/v1")
    application.include_router(orders.router, prefix="/api/v1")
    application.include_router(external_catalog.router, prefix="/api/v1")
    application.include_router(business.router, prefix="/api/v1")

    @application.get("/health", tags=["operations"])
    def health():
        return {"status": "ok"}

    @application.get("/ready", tags=["operations"])
    def ready():
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}

    application.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
