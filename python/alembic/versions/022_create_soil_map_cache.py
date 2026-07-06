"""create soil map cache table

Revision ID: 022_soil_map_cache
Revises: 02ce9fcea720
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '022_soil_map_cache'
down_revision = '02ce9fcea720'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create soil_map_cache table for NBSS API response caching"""
    op.create_table(
        'soil_map_cache',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('latitude', sa.DECIMAL(10, 8), nullable=False, comment='GPS latitude'),
        sa.Column('longitude', sa.DECIMAL(11, 8), nullable=False, comment='GPS longitude'),
        sa.Column('state', sa.String(255), nullable=True, comment='State name for district-level fallback'),
        sa.Column('district', sa.String(255), nullable=True, comment='District name for district-level fallback'),
        sa.Column('lookup_type', sa.String(50), nullable=False, comment='gps or district'),
        sa.Column('soil_type', sa.String(100), nullable=True, comment='Soil classification'),
        sa.Column('soil_texture', sa.String(100), nullable=True, comment='Soil texture'),
        sa.Column('drainage', sa.String(100), nullable=True, comment='Drainage characteristics'),
        sa.Column('slope', sa.String(100), nullable=True, comment='Slope characteristics'),
        sa.Column('ph_range', sa.String(50), nullable=True, comment='pH range'),
        sa.Column('organic_carbon_range', sa.String(50), nullable=True, comment='Organic carbon range'),
        sa.Column('confidence_score', sa.DECIMAL(3, 2), nullable=False, comment='Confidence score 0-1'),
        sa.Column('data_source', sa.String(100), nullable=False, comment='NBSS or district_average'),
        sa.Column('nbss_response', JSONB, nullable=True, comment='Complete NBSS API response'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=False, comment='Cache expiration (24 hours)'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient lookups
    op.create_index('idx_soil_map_cache_gps', 'soil_map_cache', ['latitude', 'longitude'])
    op.create_index('idx_soil_map_cache_district', 'soil_map_cache', ['state', 'district'])
    op.create_index('idx_soil_map_cache_expires', 'soil_map_cache', ['expires_at'])
    op.create_index('idx_soil_map_cache_lookup_type', 'soil_map_cache', ['lookup_type'])


def downgrade() -> None:
    """Drop soil_map_cache table"""
    op.drop_index('idx_soil_map_cache_lookup_type', table_name='soil_map_cache')
    op.drop_index('idx_soil_map_cache_expires', table_name='soil_map_cache')
    op.drop_index('idx_soil_map_cache_district', table_name='soil_map_cache')
    op.drop_index('idx_soil_map_cache_gps', table_name='soil_map_cache')
    op.drop_table('soil_map_cache')
