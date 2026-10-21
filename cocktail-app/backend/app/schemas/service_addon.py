from pydantic import BaseModel, ConfigDict, Field


class ServiceAddonFields(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=1000)
    price_cop: int = Field(ge=0, le=100000000)
    is_active: bool = True


class ServiceAddonCreate(ServiceAddonFields):
    pass


class ServiceAddonUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    price_cop: int | None = Field(default=None, ge=0, le=100000000)
    is_active: bool | None = None


class ServiceAddonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    price_cop: int
    is_active: bool
