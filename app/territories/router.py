"""HTTP-эндпоинты для работы с территориями и показателями."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.common.db import get_db
from app.territories import crud
from app.territories.schemas import (
    TerritoryCreate,
    TerritoryMetricCreate,
    TerritoryMetricRead,
    TerritoryMetricUpdate,
    TerritoryRead,
    TerritoryUpdate,
)

router = APIRouter(prefix="/territories", tags=["territories"])


# ---- Territories ----

@router.post("/", response_model=TerritoryRead, status_code=201)
def create_territory(data: TerritoryCreate, db: Session = Depends(get_db)):
    """Создать новую территорию."""
    return crud.create_territory(db, data)


@router.get("/", response_model=list[TerritoryRead])
def list_territories(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Получить список территорий."""
    return crud.list_territories(db, limit=limit, offset=offset)


@router.get("/intersects", response_model=list[TerritoryRead])
def intersecting_territories(
    wkt: str = Query(..., description="WKT-геометрия для поиска пересечений"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Найти территории, пересекающие заданную геометрию."""
    return crud.list_intersecting_territories(db, wkt=wkt, limit=limit, offset=offset)


@router.get("/{territory_id}", response_model=TerritoryRead)
def get_territory(territory_id: int, db: Session = Depends(get_db)):
    """Получить территорию по ID."""
    territory = crud.get_territory(db, territory_id)
    if territory is None:
        raise HTTPException(status_code=404, detail="Territory not found")
    return territory


@router.put("/{territory_id}", response_model=TerritoryRead)
def update_territory(
    territory_id: int, data: TerritoryUpdate, db: Session = Depends(get_db)
):
    """Обновить территорию."""
    territory = crud.update_territory(db, territory_id, data)
    if territory is None:
        raise HTTPException(status_code=404, detail="Territory not found")
    return territory


@router.delete("/{territory_id}", status_code=204)
def delete_territory(territory_id: int, db: Session = Depends(get_db)):
    """Удалить территорию."""
    deleted = crud.delete_territory(db, territory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Territory not found")


# ---- Territory Metrics ----

@router.post(
    "/{territory_id}/metrics",
    response_model=TerritoryMetricRead,
    status_code=201,
)
def create_metric(
    territory_id: int,
    data: TerritoryMetricCreate,
    db: Session = Depends(get_db),
):
    """Создать показатель для территории."""
    territory = crud.get_territory(db, territory_id)
    if territory is None:
        raise HTTPException(status_code=404, detail="Territory not found")
    return crud.create_metric(db, territory_id, data)


@router.get(
    "/{territory_id}/metrics",
    response_model=list[TerritoryMetricRead],
)
def list_metrics(territory_id: int, db: Session = Depends(get_db)):
    """Получить показатели территории."""
    territory = crud.get_territory(db, territory_id)
    if territory is None:
        raise HTTPException(status_code=404, detail="Territory not found")
    return crud.list_metrics_by_territory(db, territory_id)


@router.put(
    "/{territory_id}/metrics/{metric_id}",
    response_model=TerritoryMetricRead,
)
def update_metric(
    territory_id: int,
    metric_id: int,
    data: TerritoryMetricUpdate,
    db: Session = Depends(get_db),
):
    """Обновить показатель."""
    metric = crud.update_metric(db, metric_id, data)
    if metric is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.delete("/{territory_id}/metrics/{metric_id}", status_code=204)
def delete_metric(
    territory_id: int,
    metric_id: int,
    db: Session = Depends(get_db),
):
    """Удалить показатель."""
    deleted = crud.delete_metric(db, metric_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Metric not found")