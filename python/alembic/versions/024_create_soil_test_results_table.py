"""create soil_test_results table

Revision ID: 024_soil_test_results
Revises: 023
Create Date: 2026-02-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '024_soil_test_results'
down_revision = '023'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create soil_test_results table for storing detailed soil chemistry data"""
    
    op.create_table(
        'soil_test_results',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('farm_id', sa.BigInteger(), nullable=False),
        sa.Column('plot_id', sa.BigInteger(), nullable=True, comment='Optional specific plot'),
        
        # Test metadata
        sa.Column('test_date', sa.TIMESTAMP(), nullable=False, comment='Date of soil test'),
        sa.Column('lab_name', sa.String(255), nullable=True, comment='Testing laboratory name'),
        sa.Column('lab_reference_number', sa.String(255), nullable=True, comment='Lab reference/report number'),
        
        # Macronutrients
        sa.Column('nitrogen_kg_per_ha', sa.DECIMAL(10, 2), nullable=True, comment='Nitrogen content (kg/ha)'),
        sa.Column('phosphorus_kg_per_ha', sa.DECIMAL(10, 2), nullable=True, comment='Phosphorus content (kg/ha)'),
        sa.Column('potassium_kg_per_ha', sa.DECIMAL(10, 2), nullable=True, comment='Potassium content (kg/ha)'),
        
        # Soil properties
        sa.Column('ph_level', sa.DECIMAL(4, 2), nullable=True, comment='Soil pH level (0-14)'),
        sa.Column('organic_carbon_percent', sa.DECIMAL(5, 2), nullable=True, comment='Organic carbon percentage'),
        sa.Column('organic_matter_percent', sa.DECIMAL(5, 2), nullable=True, comment='Organic matter percentage'),
        sa.Column('electrical_conductivity', sa.DECIMAL(6, 2), nullable=True, comment='EC (dS/m) - salinity indicator'),
        
        # Micronutrients
        sa.Column('sulfur_ppm', sa.DECIMAL(10, 2), nullable=True, comment='Sulfur content (ppm)'),
        sa.Column('zinc_ppm', sa.DECIMAL(10, 2), nullable=True, comment='Zinc content (ppm)'),
        sa.Column('iron_ppm', sa.DECIMAL(10, 2), nullable=True, comment='Iron content (ppm)'),
        sa.Column('manganese_ppm', sa.DECIMAL(10, 2), nullable=True, comment='Manganese content (ppm)'),
        sa.Column('copper_ppm', sa.DECIMAL(10, 2), nullable=True, comment='Copper content (ppm)'),
        sa.Column('boron_ppm', sa.DECIMAL(10, 2), nullable=True, comment='Boron content (ppm)'),
        
        # Calculated scores
        sa.Column('soil_health_score', sa.DECIMAL(5, 2), nullable=True, comment='Calculated soil health score (0-100)'),
        
        # Additional data
        sa.Column('test_method', sa.String(255), nullable=True, comment='Testing method used'),
        sa.Column('raw_data_json', sa.Text(), nullable=True, comment='Raw test data in JSON format'),
        sa.Column('recommendations', sa.Text(), nullable=True, comment='Lab recommendations'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes'),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('enable', sa.SmallInteger(), server_default='1', nullable=False),
        
        # Primary key
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], name='fk_soil_test_results_farm_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plot_id'], ['farm_plots.id'], name='fk_soil_test_results_plot_id', ondelete='CASCADE'),
    )
    
    # Create indexes for efficient querying
    op.create_index('ix_soil_test_results_farm_id', 'soil_test_results', ['farm_id'])
    op.create_index('ix_soil_test_results_plot_id', 'soil_test_results', ['plot_id'])
    op.create_index('ix_soil_test_results_test_date', 'soil_test_results', ['test_date'])
    op.create_index('ix_soil_test_results_farm_test_date', 'soil_test_results', ['farm_id', 'test_date'])
    op.create_index('ix_soil_test_results_lab_reference', 'soil_test_results', ['lab_reference_number'])


def downgrade() -> None:
    """Drop soil_test_results table"""
    
    op.drop_index('ix_soil_test_results_lab_reference', table_name='soil_test_results')
    op.drop_index('ix_soil_test_results_farm_test_date', table_name='soil_test_results')
    op.drop_index('ix_soil_test_results_test_date', table_name='soil_test_results')
    op.drop_index('ix_soil_test_results_plot_id', table_name='soil_test_results')
    op.drop_index('ix_soil_test_results_farm_id', table_name='soil_test_results')
    op.drop_table('soil_test_results')
