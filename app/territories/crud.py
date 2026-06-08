"""CRUD-функции для работы с территориями и показателями."""

from geoalchemy2 import WKTElement
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.territories.models import Territory, TerritoryMetric
from app.territories.schemas import (
    TerritoryCreate,
    TerritoryMetricCreate,
    TerritoryMetricUpdate,
    TerritoryUpdate,
)


# ---- Вспомогательная функция ----

def _territory_select():
    """Базовый SELECT для территории с геометрией как WKT."""
    return select(
        Territory.id,
        Territory.name,
        Territory.territory_type,
        Territory.level,
        Territory.description,
        func.ST_AsText(Territory.geom).label("geom_wkt"),
        Territory.created_at,
    )


def _territory_to_dict(row):
    """Преобразует строку результата в словарь."""
    return {
        "id": row.id,
        "name": row.name,
        "territory_type": row.territory_type,
        "level": row.level,
        "description": row.description,
        "geom_wkt": row.geom_wkt,
        "created_at": row.created_at,
    }


# ---- Territories CRUD ----

def get_territory(db: Session, territory_id: int) -> dict | None:
    """Получить территорию по ID."""
    stmt = _territory_select().where(Territory.id == territory_id)
    row = db.execute(stmt).first()
    return _territory_to_dict(row) if row else None


def list_territories(db: Session, limit: int = 100, offset: int = 0) -> list[dict]:
    """Получить список территорий."""
    stmt = _territory_select().order_by(Territory.id).limit(limit).offset(offset)
    rows = db.execute(stmt).all()
    return [_territory_to_dict(row) for row in rows]


def create_territory(db: Session, data: TerritoryCreate) -> dict:
    """Создать новую территорию."""
    # Находим максимальный ID и увеличиваем на 1
    max_id = db.execute(select(func.max(Territory.id))).scalar() or 0
    territory = Territory(
        id=max_id + 1,
        name=data.name,
        territory_type=data.territory_type,
        level=data.level,
        description=data.description,
        geom=WKTElement(data.geom_wkt, srid=4326),
    )
    db.add(territory)
    db.commit()
    db.refresh(territory)
    return get_territory(db, territory.id)


def update_territory(
    db: Session, territory_id: int, data: TerritoryUpdate
) -> dict | None:
    """Обновить территорию."""
    territory = db.query(Territory).filter(Territory.id == territory_id).first()
    if territory is None:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "geom_wkt" in update_data:
        territory.geom = WKTElement(update_data.pop("geom_wkt"), srid=4326)

    for field, value in update_data.items():
        setattr(territory, field, value)

    db.commit()
    db.refresh(territory)
    return get_territory(db, territory.id)


def delete_territory(db: Session, territory_id: int) -> bool:
    """Удалить территорию."""
    territory = db.query(Territory).filter(Territory.id == territory_id).first()
    if territory is None:
        return False
    db.delete(territory)
    db.commit()
    return True


def list_intersecting_territories(
    db: Session, wkt: str, limit: int = 100, offset: int = 0
) -> list[dict]:
    """Найти территории, пересекающие заданную WKT-геометрию."""
    search_geom = WKTElement(wkt, srid=4326)
    stmt = (
        _territory_select()
        .where(func.ST_Intersects(Territory.geom, search_geom))
        .order_by(Territory.id)
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).all()
    return [_territory_to_dict(row) for row in rows]


# ---- Territory Metrics CRUD ----

def create_metric(
    db: Session, territory_id: int, data: TerritoryMetricCreate
) -> TerritoryMetric:
    """Создать показатель для территории."""
    metric = TerritoryMetric(
        territory_id=territory_id,
        year=data.year,
        population=data.population,
        area_km2=data.area_km2,
        source=data.source,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def list_metrics_by_territory(
    db: Session, territory_id: int
) -> list[TerritoryMetric]:
    """Получить все показатели территории."""
    return (
        db.query(TerritoryMetric)
        .filter(TerritoryMetric.territory_id == territory_id)
        .order_by(TerritoryMetric.year)
        .all()
    )


def update_metric(
    db: Session, metric_id: int, data: TerritoryMetricUpdate
) -> TerritoryMetric | None:
    """Обновить показатель."""
    metric = db.query(TerritoryMetric).filter(TerritoryMetric.id == metric_id).first()
    if metric is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(metric, field, value)

    db.commit()
    db.refresh(metric)
    return metric


def delete_metric(db: Session, metric_id: int) -> bool:
    """Удалить показатель."""
    metric = db.query(TerritoryMetric).filter(TerritoryMetric.id == metric_id).first()
    if metric is None:
        return False
    db.delete(metric)
    db.commit()
    return True