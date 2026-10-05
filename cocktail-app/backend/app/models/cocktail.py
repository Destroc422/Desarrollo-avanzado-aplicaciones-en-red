from sqlalchemy import Column, Integer, String, Text
from ..database.session import Base

class CocktailModel(Base):
    __tablename__ = "cocktails"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    ingredients = Column(Text) # Guardaremos como string separado por comas o JSON
    image = Column(String)
