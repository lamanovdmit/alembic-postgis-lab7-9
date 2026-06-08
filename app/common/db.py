"""Подключение к базе данных."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://urban_user:urban_password@db:5432/urban_data",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Базовый класс для ORM-моделей."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Генератор сессий базы данных для Dependency Injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()