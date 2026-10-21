from sqlalchemy import inspect, text

from .session import Base


_SQLITE_COLUMNS = {
    "users": {
        "email": "VARCHAR(255)",
        "full_name": "VARCHAR(120) NOT NULL DEFAULT ''",
        "phone": "VARCHAR(30) NOT NULL DEFAULT ''",
        "national_id": "VARCHAR(30) NOT NULL DEFAULT ''",
        "address": "VARCHAR(250) NOT NULL DEFAULT ''",
        "city": "VARCHAR(80) NOT NULL DEFAULT ''",
        "is_active": "BOOLEAN NOT NULL DEFAULT 1",
    },
    "cocktails": {
        "category": "VARCHAR(80) NOT NULL DEFAULT 'Cócteles'",
        "price_cop": "INTEGER NOT NULL DEFAULT 0",
        "estimated_cost_cop": "INTEGER NOT NULL DEFAULT 0",
        "instructions": "TEXT NOT NULL DEFAULT ''",
        "is_available": "BOOLEAN NOT NULL DEFAULT 1",
    },
}


def upgrade_existing_sqlite_schema(engine) -> None:
    """Apply additive changes so existing SQLite data remains available."""
    if engine.dialect.name != "sqlite":
        return

    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        tables = set(inspect(connection).get_table_names())
        if "users" in tables:
            columns = {column["name"] for column in inspect(connection).get_columns("users")}
            legacy_accounts = "email" not in columns or "full_name" not in columns
            for name, definition in _SQLITE_COLUMNS["users"].items():
                if name not in columns:
                    connection.exec_driver_sql(f"ALTER TABLE users ADD COLUMN {name} {definition}")
            connection.exec_driver_sql(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email_unique "
                "ON users(email) WHERE email IS NOT NULL AND email <> ''"
            )
            # The old app created an admin/admin account. Demote old roles once,
            # during the schema transition, while leaving bootstrapped admins intact.
            if legacy_accounts:
                connection.execute(text("UPDATE users SET role = 'customer' WHERE role = 'admin'"))

        if "cocktails" in tables:
            columns = {column["name"] for column in inspect(connection).get_columns("cocktails")}
            for name, definition in _SQLITE_COLUMNS["cocktails"].items():
                if name not in columns:
                    connection.exec_driver_sql(f"ALTER TABLE cocktails ADD COLUMN {name} {definition}")
            connection.execute(text("UPDATE cocktails SET is_available = 0 WHERE price_cop <= 0"))
