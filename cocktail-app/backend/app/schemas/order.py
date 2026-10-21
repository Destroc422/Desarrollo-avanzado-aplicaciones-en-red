from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class OrderLineCreate(BaseModel):
    cocktail_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=30)


class OrderCreate(BaseModel):
    items: list[OrderLineCreate] = Field(min_length=1, max_length=30)
    addon_ids: list[int] = Field(default_factory=list, max_length=20)
    delivery_address: str = Field(min_length=5, max_length=250)
    delivery_scheduled_at: datetime | None = None
    delivery_notes: str = Field(default="", max_length=500)
    additional_service: str = Field(default="", max_length=300)
    payment_method: Literal["wompi", "cash_on_delivery"] = "cash_on_delivery"

    @field_validator("addon_ids")
    @classmethod
    def unique_addons(cls, value: list[int]) -> list[int]:
        if any(item <= 0 for item in value):
            raise ValueError("Los servicios adicionales seleccionados no son válidos.")
        if len(set(value)) != len(value):
            raise ValueError("No repitas un servicio adicional.")
        return value


class OrderStatusUpdate(BaseModel):
    status: Literal["confirmed", "preparing", "out_for_delivery", "delivered", "cancelled"]


class OrderRead(BaseModel):
    id: int
    items: list[dict]
    addons: list[dict]
    total_cop: int
    payment_method: str
    payment_status: str
    status: str
    delivery_address: str
    delivery_scheduled_at: datetime | None
    delivery_notes: str
    additional_service: str
    created_at: datetime
    customer_username: str | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None
