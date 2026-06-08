"""create territories and metrics tables

Revision ID: 001_create_territories_metrics
Revises: 
Create Date: 2026-04-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "territories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("territory_type", sa.String(length=100), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column(
            "geom",
            Geometry(
                geometry_type="MULTIPOLYGON",
                srid=4326,
                spatial_index=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("level >= 0", name="ck_territories_level_non_negative"),
    )

    op.create_index(
        "idx_territories_geom",
        "territories",
        ["geom"],
        postgresql_using="gist",
    )

    op.create_table(
        "territory_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("territory_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("population", sa.Integer(), nullable=True),
        sa.Column("area_km2", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["territory_id"],
            ["territories.id"],
            name="fk_territory_metrics_territory_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "territory_id",
            "year",
            name="uq_territory_metrics_territory_year",
        ),
    )

    op.create_index(
        "idx_territory_metrics_territory_id",
        "territory_metrics",
        ["territory_id"],
    )

    op.execute(
        """
        INSERT INTO territories (id, name, territory_type, level, geom)
        VALUES
        (
            1,
            'Тестовый район А',
            'district',
            1,
            ST_GeomFromText(
                'MULTIPOLYGON(((30.20 59.90, 30.50 59.90, 30.50 60.10, 30.20 60.10, 30.20 59.90)))',
                4326
            )
        ),
        (
            2,
            'Тестовый район Б',
            'district',
            1,
            ST_GeomFromText(
                'MULTIPOLYGON(((30.50 59.90, 30.80 59.90, 30.80 60.10, 30.50 60.10, 30.50 59.90)))',
                4326
            )
        );
        """
    )

    op.execute(
        """
        INSERT INTO territory_metrics (territory_id, year, population, area_km2, source)
        VALUES
        (1, 2025, 120000, 34.50, 'test dataset'),
        (2, 2025, 95000, 28.70, 'test dataset');
        """
    )


def downgrade() -> None:
    op.drop_index("idx_territory_metrics_territory_id", table_name="territory_metrics")
    op.drop_table("territory_metrics")

    op.drop_index("idx_territories_geom", table_name="territories")
    op.drop_table("territories")