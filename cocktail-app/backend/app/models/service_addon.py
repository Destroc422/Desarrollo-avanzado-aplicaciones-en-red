from sqlalchemy import Boolean, Column, Integer, String, Text
from ..database.session import Base


class ServiceAddonModel(Base):
    __tablename__ = "service_addons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False, default="")
    price_cop = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
