"""create fertilizer_applications table

Revision ID: 025
Revises: 024
Create Date: 2024-02-22

Task 24.2: Build fertilizer tracking system
Validates: Requirements AC9 (Phase 6 - Required)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '025'
down_revision = '024_soil_test_results'
branch_labels = None
depends_on = None


def upgrade():
    """Create fertilizer_applications table"""
    op.create_table(
        'fertilizer_applications',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('farm_id', sa.BigInteger(), nullable=False),
        sa.Column('plot_id', sa.BigInteger(), nullable=True, comment='Optional specific plot'),
        sa.Column('crop_id', sa.BigInteger(), nullable=True, comment='Associated crop if applicable'),
        
        # Application details
        sa.Column('application_date', sa.Date(), nullable=False, comment='Date of fertilizer application'),
        sa.Column('fertilizer_type', sa.String(100), nullable=False, comment='Type: urea, dap, mop, vermicompost, etc.'),
        sa.Column('category', sa.String(50), nullable=False, comment='Category: organic or chemical'),
        
        # Quantities
        sa.Column('quantity_kg', sa.DECIMAL(10, 2), nullable=False, comment='Total quantity applied (kg)'),
        sa.Column('quantity_per_hectare', sa.DECIMAL(10, 2), nullable=True, comment='Quantity per hectare (kg/ha)'),
        sa.Column('area_applied_hectares', sa.DECIMAL(10, 2), nullable=True, comment='Area where fertilizer was applied'),
        
        # Nutrients provided
        sa.Column('nitrogen_kg', sa.DECIMAL(10, 2), nullable=True, comment='Nitrogen provided (kg)'),
        sa.Column('phosphorus_kg', sa.DECIMAL(10, 2), nullable=True, comment='Phosphorus provided (kg)'),
        sa.Column('potassium_kg', sa.DECIMAL(10, 2), nullable=True, comment='Potassium provided (kg)'),
        
        # Cost tracking
        sa.Column('cost_total', sa.DECIMAL(10, 2), nullable=True, comment='Total cost (₹)'),
        sa.Column('cost_per_kg', sa.DECIMAL(10, 2), nullable=True, comment='Cost per kg (₹)'),
        sa.Column('cost_per_hectare', sa.DECIMAL(10, 2), nullable=True, comment='Cost per hectare (₹)'),
        
        # Application method and timing
        sa.Column('application_method', sa.String(255), nullable=True, comment='Method: broadcast, banding, foliar, etc.'),
        sa.Column('growth_stage', sa.String(100), nullable=True, comment='Crop growth stage: basal, vegetative, flowering'),
        sa.Column('days_after_planting', sa.BigInteger(), nullable=True, comment='Days after planting when applied'),
        
        # Soil test linkage
        sa.Column('soil_test_before_id', sa.BigInteger(), nullable=True, comment='Soil test before application'),
        sa.Column('soil_test_after_id', sa.BigInteger(), nullable=True, comment='Soil test after application'),
        
        # Effectiveness tracking
        sa.Column('effectiveness_score', sa.DECIMAL(5, 2), nullable=True, comment='Effectiveness score (0-100) based on soil response'),
        sa.Column('soil_response_notes', sa.Text(), nullable=True, comment='Observed soil response and crop performance'),
        
        # Weather conditions
        sa.Column('weather_conditions', sa.String(255), nullable=True, comment='Weather during application'),
        sa.Column('temperature_celsius', sa.DECIMAL(5, 2), nullable=True, comment='Temperature during application'),
        sa.Column('rainfall_mm_24h', sa.DECIMAL(6, 2), nullable=True, comment='Rainfall within 24 hours after application'),
        
        # Recommendations and notes
        sa.Column('recommended_by', sa.String(255), nullable=True, comment='Source: system, agronomist, farmer'),
        sa.Column('recommendation_id', sa.String(255), nullable=True, comment='Reference to recommendation that suggested this'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes'),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('enable', sa.SmallInteger(), server_default='1', nullable=False),
        
        # Primary key
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plot_id'], ['farm_plots.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['crop_id'], ['crops.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['soil_test_before_id'], ['soil_test_results.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['soil_test_after_id'], ['soil_test_results.id'], ondelete='SET NULL'),
    )
    
    # Create indexes for common queries
    op.create_index('ix_fertilizer_applications_farm_id', 'fertilizer_applications', ['farm_id'])
    op.create_index('ix_fertilizer_applications_plot_id', 'fertilizer_applications', ['plot_id'])
    op.create_index('ix_fertilizer_applications_crop_id', 'fertilizer_applications', ['crop_id'])
    op.create_index('ix_fertilizer_applications_application_date', 'fertilizer_applications', ['application_date'])
    op.create_index('ix_fertilizer_applications_fertilizer_type', 'fertilizer_applications', ['fertilizer_type'])
    op.create_index('ix_fertilizer_applications_category', 'fertilizer_applications', ['category'])
    
    # Composite index for common query patterns
    op.create_index(
        'ix_fertilizer_applications_farm_date',
        'fertilizer_applications',
        ['farm_id', 'application_date']
    )


def downgrade():
    """Drop fertilizer_applications table"""
    op.drop_index('ix_fertilizer_applications_farm_date', table_name='fertilizer_applications')
    op.drop_index('ix_fertilizer_applications_category', table_name='fertilizer_applications')
    op.drop_index('ix_fertilizer_applications_fertilizer_type', table_name='fertilizer_applications')
    op.drop_index('ix_fertilizer_applications_application_date', table_name='fertilizer_applications')
    op.drop_index('ix_fertilizer_applications_crop_id', table_name='fertilizer_applications')
    op.drop_index('ix_fertilizer_applications_plot_id', table_name='fertilizer_applications')
    op.drop_index('ix_fertilizer_applications_farm_id', table_name='fertilizer_applications')
    op.drop_table('fertilizer_applications')
