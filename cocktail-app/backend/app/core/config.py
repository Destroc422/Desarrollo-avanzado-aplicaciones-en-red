from pathlib import Path
import os


BACKEND_DIR = Path(__file__).resolve().parents[2]


def _load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE pairs without overriding the process environment."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name.isidentifier():
            os.environ.setdefault(name, value)


_load_env_file(BACKEND_DIR / ".env")


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
if len(SECRET_KEY) < 32 or SECRET_KEY in {
    "GRILLO_SECRET_KEY_SUPER_SECRET_2026",
    "change-me",
    "secret",
}:
    raise RuntimeError("SECRET_KEY must contain at least 32 non-default characters. Configure backend/.env.")

ALGORITHM = os.getenv("ALGORITHM", "HS256").strip()
if ALGORITHM != "HS256":
    raise RuntimeError("ALGORITHM must be HS256.")

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
except ValueError as exc:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be an integer.") from exc
if not 5 <= ACCESS_TOKEN_EXPIRE_MINUTES <= 1440:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be between 5 and 1440.")

_database_url = os.getenv("DATABASE_URL", "").strip()
if not _database_url:
    _database_url = f"sqlite:///{(BACKEND_DIR / 'cocktails.db').as_posix()}"
elif _database_url.startswith("sqlite:///"):
    sqlite_path = _database_url[len("sqlite:///"):]
    if sqlite_path.startswith("./") or (not Path(sqlite_path).is_absolute() and not sqlite_path.startswith("/")):
        resolved = (BACKEND_DIR / sqlite_path).resolve()
        _database_url = f"sqlite:///{resolved.as_posix()}"
DATABASE_URL = _database_url

_upload_dir = Path(os.getenv("UPLOAD_DIR", str(BACKEND_DIR / "uploads"))).expanduser()
UPLOAD_DIR = (_upload_dir if _upload_dir.is_absolute() else BACKEND_DIR / _upload_dir).resolve()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").strip().rstrip("/")
_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
FRONTEND_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv("FRONTEND_ORIGINS", _default_origins).split(",")
    if origin.strip()
]
COOKIE_SECURE = _env_bool("COOKIE_SECURE", ENVIRONMENT == "production")
COOKIE_NAME = "elgrillo_session"

BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Estanco y Coctelería El Grillo").strip()
BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "").strip()
BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "").strip()
BUSINESS_ADDRESS = os.getenv("BUSINESS_ADDRESS", "").strip()
BUSINESS_INSTAGRAM = os.getenv("BUSINESS_INSTAGRAM", "").strip()
BUSINESS_FACEBOOK = os.getenv("BUSINESS_FACEBOOK", "").strip()
BUSINESS_TIKTOK = os.getenv("BUSINESS_TIKTOK", "").strip()

WOMPI_PUBLIC_KEY = os.getenv("WOMPI_PUBLIC_KEY", "").strip()
WOMPI_INTEGRITY_SECRET = os.getenv("WOMPI_INTEGRITY_SECRET", "").strip()
WOMPI_EVENTS_SECRET = os.getenv("WOMPI_EVENTS_SECRET", "").strip()
WOMPI_ENVIRONMENT = os.getenv("WOMPI_ENVIRONMENT", "sandbox").strip().lower()
