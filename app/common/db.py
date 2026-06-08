"""Подключение к базе данных."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

engine = create_engine(
    "postgresql+psycopg://urban_user:urban_password@localhost:5433/urban_data",
    pool_pre_ping=True,
)

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