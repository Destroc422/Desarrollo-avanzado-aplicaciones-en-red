from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: str = Field(min_length=5, max_length=255)
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=30)
    national_id: str = Field(min_length=4, max_length=30)
    address: str = Field(min_length=5, max_length=250)
    city: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized.count("@") != 1 or "." not in normalized.split("@", 1)[1]:
            raise ValueError("Ingresa un correo electrónico válido.")
        return normalized

    @field_validator("password")
    @classmethod
    def bcrypt_compatible_password(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar 72 bytes.")
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None = None
    full_name: str
    phone: str
    national_id: str
    address: str
    city: str
    role: str
    is_active: bool
