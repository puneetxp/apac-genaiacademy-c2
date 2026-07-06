"""create weather data tables

Revision ID: 023
Revises: 022_soil_map_cache
Create Date: 2026-02-24 14:00:00.000000

Task 23.1: Integrate with Weather APIs
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '023'
down_revision = '022_soil_map_cache'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create weather data storage tables"""

    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    def index_absent(name: str) -> bool:
        existing_indexes = set()
        for table in ('weather_forecasts', 'weather_history', 'weather_current_cache', 'weather_alerts_cache'):
            try:
                idx = inspector.get_indexes(table)
                existing_indexes.update(i['name'] for i in idx)
            except Exception:
                continue
        return name not in existing_indexes

    def create_weather_forecasts():
        op.create_table(
            'weather_forecasts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('latitude', sa.Float(), nullable=False),
            sa.Column('longitude', sa.Float(), nullable=False),
            sa.Column('forecast_date', sa.Date(), nullable=False),
            sa.Column('temp_min', sa.Float(), nullable=True),
            sa.Column('temp_max', sa.Float(), nullable=True),
            sa.Column('humidity', sa.Integer(), nullable=True),
            sa.Column('rainfall', sa.Float(), nullable=True),
            sa.Column('wind_speed', sa.Float(), nullable=True),
            sa.Column('description', sa.String(255), nullable=True),
            sa.Column('source', sa.String(50), nullable=False),
            sa.Column('retrieved_at', sa.DateTime(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )

        if index_absent('ix_weather_forecasts_location'):
            op.create_index(
                'ix_weather_forecasts_location',
                'weather_forecasts',
                ['latitude', 'longitude']
            )
        if index_absent('ix_weather_forecasts_date'):
            op.create_index(
                'ix_weather_forecasts_date',
                'weather_forecasts',
                ['forecast_date']
            )
        if index_absent('ix_weather_forecasts_retrieved'):
            op.create_index(
                'ix_weather_forecasts_retrieved',
                'weather_forecasts',
                ['retrieved_at']
            )

    def create_weather_history():
        op.create_table(
            'weather_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('latitude', sa.Float(), nullable=False),
            sa.Column('longitude', sa.Float(), nullable=False),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('temp_min', sa.Float(), nullable=True),
            sa.Column('temp_max', sa.Float(), nullable=True),
            sa.Column('temp_avg', sa.Float(), nullable=True),
            sa.Column('humidity', sa.Integer(), nullable=True),
            sa.Column('rainfall', sa.Float(), nullable=True),
            sa.Column('wind_speed', sa.Float(), nullable=True),
            sa.Column('source', sa.String(50), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('latitude', 'longitude', 'date', 'source', name='uq_weather_history_location_date_source')
        )

        if index_absent('ix_weather_history_location'):
            op.create_index(
                'ix_weather_history_location',
                'weather_history',
                ['latitude', 'longitude']
            )
        if index_absent('ix_weather_history_date'):
            op.create_index(
                'ix_weather_history_date',
                'weather_history',
                ['date']
            )

    def create_weather_current_cache():
        op.create_table(
            'weather_current_cache',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('latitude', sa.Float(), nullable=False),
            sa.Column('longitude', sa.Float(), nullable=False),
            sa.Column('temperature', sa.Float(), nullable=True),
            sa.Column('feels_like', sa.Float(), nullable=True),
            sa.Column('humidity', sa.Integer(), nullable=True),
            sa.Column('pressure', sa.Integer(), nullable=True),
            sa.Column('wind_speed', sa.Float(), nullable=True),
            sa.Column('wind_direction', sa.Integer(), nullable=True),
            sa.Column('rainfall', sa.Float(), nullable=True),
            sa.Column('description', sa.String(255), nullable=True),
            sa.Column('source', sa.String(50), nullable=False),
            sa.Column('timestamp', sa.DateTime(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('latitude', 'longitude', name='uq_weather_current_location')
        )

        if index_absent('ix_weather_current_location'):
            op.create_index(
                'ix_weather_current_location',
                'weather_current_cache',
                ['latitude', 'longitude']
            )
        if index_absent('ix_weather_current_expires'):
            op.create_index(
                'ix_weather_current_expires',
                'weather_current_cache',
                ['expires_at']
            )

    def create_weather_alerts_cache():
        op.create_table(
            'weather_alerts_cache',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('alert_id', sa.String(255), nullable=False),
            sa.Column('latitude', sa.Float(), nullable=True),
            sa.Column('longitude', sa.Float(), nullable=True),
            sa.Column('state', sa.String(100), nullable=True),
            sa.Column('district', sa.String(100), nullable=True),
            sa.Column('severity', sa.String(20), nullable=False),
            sa.Column('event_type', sa.String(100), nullable=False),
            sa.Column('headline', sa.String(500), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('start_time', sa.DateTime(), nullable=False),
            sa.Column('end_time', sa.DateTime(), nullable=False),
            sa.Column('affected_areas', postgresql.JSONB(), nullable=True),
            sa.Column('source', sa.String(50), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )

        if index_absent('ix_weather_alerts_cache_location'):
            op.create_index(
                'ix_weather_alerts_cache_location',
                'weather_alerts_cache',
                ['latitude', 'longitude']
            )
        if index_absent('ix_weather_alerts_cache_state_district'):
            op.create_index(
                'ix_weather_alerts_cache_state_district',
                'weather_alerts_cache',
                ['state', 'district']
            )
        if index_absent('ix_weather_alerts_cache_severity'):
            op.create_index(
                'ix_weather_alerts_cache_severity',
                'weather_alerts_cache',
                ['severity']
            )
        if index_absent('ix_weather_alerts_cache_time'):
            op.create_index(
                'ix_weather_alerts_cache_time',
                'weather_alerts_cache',
                ['start_time', 'end_time']
            )

    if 'weather_forecasts' not in existing_tables:
        create_weather_forecasts()

    if 'weather_history' not in existing_tables:
        create_weather_history()

    if 'weather_current_cache' not in existing_tables:
        create_weather_current_cache()

    if 'weather_alerts_cache' not in existing_tables:
        create_weather_alerts_cache()


def downgrade() -> None:
    """Drop weather data storage tables"""
    op.drop_table('weather_alerts_cache')
    op.drop_table('weather_current_cache')
    op.drop_table('weather_history')
    op.drop_table('weather_forecasts')
