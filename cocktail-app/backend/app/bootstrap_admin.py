"""Create or promote the first administrator through an interactive prompt."""

from getpass import getpass

from .auth import get_password_hash
from .database.session import SessionLocal
from .database.session import engine
from .database.migrations import upgrade_existing_sqlite_schema
from .models import UserModel


def main() -> None:
    username = input("Usuario administrador: ").strip()
    if len(username) < 3 or len(username) > 50:
        raise SystemExit("El usuario debe tener entre 3 y 50 caracteres.")
    password = getpass("Contraseña (mínimo 12 caracteres): ")
    confirmation = getpass("Confirma la contraseña: ")
    if len(password) < 12 or len(password.encode("utf-8")) > 72:
        raise SystemExit("La contraseña debe tener al menos 12 caracteres y no superar 72 bytes.")
    if password != confirmation:
        raise SystemExit("Las contraseñas no coinciden.")

    db = SessionLocal()
    try:
        upgrade_existing_sqlite_schema(engine)
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user:
            user.role = "admin"
            user.is_active = True
            user.hashed_password = get_password_hash(password)
        else:
            user = UserModel(
                username=username,
                hashed_password=get_password_hash(password),
                role="admin",
                is_active=True,
            )
            db.add(user)
        db.commit()
        print(f"Administrador '{username}' listo.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
