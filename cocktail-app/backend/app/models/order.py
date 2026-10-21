from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from ..database.session import Base


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    items_json = Column(Text, nullable=False)
    addons_json = Column(Text, nullable=False, default="[]")
    total_cop = Column(Integer, nullable=False)
    payment_method = Column(String(30), nullable=False)
    payment_status = Column(String(30), nullable=False, default="pending")
    status = Column(String(30), nullable=False, default="received")
    payment_reference = Column(String(100), unique=True, nullable=False, index=True)
    payment_transaction_id = Column(String(100), nullable=True, index=True)
    delivery_address = Column(String(250), nullable=False)
    delivery_scheduled_at = Column(DateTime(timezone=True), nullable=True)
    delivery_notes = Column(String(500), nullable=False, default="")
    additional_service = Column(String(300), nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
