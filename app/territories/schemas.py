"""Pydantic-схемы для территорий и показателей."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---- Territory ----

class TerritoryBase(BaseModel):
    """Базовые поля территории."""

    name: str = Field(..., description="Название территории")
    territory_type: str = Field(..., description="Тип территории")
    level: int = Field(..., ge=0, description="Уровень территории (>= 0)")
    description: str | None = Field(None, description="Описание")
    geom_wkt: str = Field(..., description="Геометрия в формате WKT")


class TerritoryCreate(TerritoryBase):
    """Схема для создания территории."""
    pass


class TerritoryUpdate(BaseModel):
    """Схема для обновления территории (все поля необязательные)."""

    name: str | None = None
    territory_type: str | None = None
    level: int | None = Field(None, ge=0)
    description: str | None = None
    geom_wkt: str | None = None


class TerritoryRead(BaseModel):
    """Схема для чтения территории."""

    id: int
    name: str
    territory_type: str
    level: int
    description: str | None
    geom_wkt: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---- TerritoryMetric ----

class TerritoryMetricCreate(BaseModel):
    """Схема для создания показателя."""

    year: int = Field(..., description="Год")
    population: int | None = Field(None, description="Население")
    area_km2: float | None = Field(None, description="Площадь в км²")
    source: str | None = Field(None, description="Источник данных")


class TerritoryMetricUpdate(BaseModel):
    """Схема для обновления показателя (все поля необязательные)."""

    year: int | None = None
    population: int | None = None
    area_km2: float | None = None
    source: str | None = None


class TerritoryMetricRead(BaseModel):
    """Схема для чтения показателя."""

    id: int
    territory_id: int
    year: int
    population: int | None
    area_km2: float | None
    source: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)