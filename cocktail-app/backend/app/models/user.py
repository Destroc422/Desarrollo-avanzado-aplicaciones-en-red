from sqlalchemy import Boolean, Column, Integer, String
from ..database.session import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    full_name = Column(String(120), nullable=False, default="")
    phone = Column(String(30), nullable=False, default="")
    national_id = Column(String(30), nullable=False, default="")
    address = Column(String(250), nullable=False, default="")
    city = Column(String(80), nullable=False, default="")
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="customer")
    is_active = Column(Boolean, nullable=False, default=True)
