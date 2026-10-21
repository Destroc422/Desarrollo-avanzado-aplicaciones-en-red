from sqlalchemy import Boolean, Column, Integer, String, Text
from ..database.session import Base


class CocktailModel(Base):
    __tablename__ = "cocktails"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), index=True, nullable=False)
    description = Column(Text, nullable=False, default="")
    category = Column(String(80), nullable=False, default="Cócteles")
    price_cop = Column(Integer, nullable=False, default=0)
    estimated_cost_cop = Column(Integer, nullable=False, default=0)
    ingredients = Column(Text, nullable=False, default="[]")
    instructions = Column(Text, nullable=False, default="")
    image = Column(String(500), nullable=False, default="")
    is_available = Column(Boolean, nullable=False, default=True)
