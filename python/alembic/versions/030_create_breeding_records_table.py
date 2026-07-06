"""create breeding records table

Revision ID: 030
Revises: 029
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '030'
down_revision = '026'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create breeding records table"""
    op.create_table(
        'breeding_records',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('livestock_id', sa.BigInteger(), nullable=False, comment='Parent livestock ID'),
        sa.Column('farmer_id', sa.BigInteger(), nullable=False, comment='Farmer/owner ID'),
        sa.Column('breeding_type', sa.String(50), nullable=False, comment='natural, artificial_insemination'),
        sa.Column('breeding_date', sa.Date(), nullable=False, comment='Date of breeding'),
        sa.Column('mate_id', sa.BigInteger(), nullable=True, comment='Mate livestock ID if known'),
        sa.Column('mate_breed', sa.String(255), nullable=True, comment='Mate breed if external'),
        sa.Column('expected_delivery_date', sa.Date(), nullable=True, comment='Expected calving/kidding date'),
        sa.Column('actual_delivery_date', sa.Date(), nullable=True, comment='Actual delivery date'),
        sa.Column('pregnancy_status', sa.String(50), nullable=False, default='pending', comment='pending, confirmed, delivered, failed'),
        sa.Column('number_of_offspring', sa.Integer(), nullable=True, comment='Number of offspring born'),
        sa.Column('breeding_cost', sa.DECIMAL(10, 2), nullable=True, comment='Cost of breeding service'),
        sa.Column('veterinarian_name', sa.String(255), nullable=True, comment='Veterinarian name'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('enable', sa.Integer(), server_default='1', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['livestock_id'], ['livestock.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['farmer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mate_id'], ['livestock.id'], ondelete='SET NULL'),
    )
    
    # Create indexes
    op.create_index('idx_breeding_records_livestock_id', 'breeding_records', ['livestock_id'])
    op.create_index('idx_breeding_records_farmer_id', 'breeding_records', ['farmer_id'])
    op.create_index('idx_breeding_records_breeding_date', 'breeding_records', ['breeding_date'])
    op.create_index('idx_breeding_records_pregnancy_status', 'breeding_records', ['pregnancy_status'])
    
    # Create offspring table
    op.create_table(
        'offspring',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('breeding_record_id', sa.BigInteger(), nullable=False, comment='Breeding record ID'),
        sa.Column('livestock_id', sa.BigInteger(), nullable=True, comment='Livestock ID if registered'),
        sa.Column('farmer_id', sa.BigInteger(), nullable=False, comment='Farmer/owner ID'),
        sa.Column('birth_date', sa.Date(), nullable=False, comment='Date of birth'),
        sa.Column('gender', sa.String(20), nullable=True, comment='male, female'),
        sa.Column('birth_weight', sa.DECIMAL(10, 2), nullable=True, comment='Birth weight in kg'),
        sa.Column('health_status', sa.String(50), nullable=False, default='healthy', comment='healthy, weak, deceased'),
        sa.Column('current_weight', sa.DECIMAL(10, 2), nullable=True, comment='Current weight in kg'),
        sa.Column('growth_rate', sa.DECIMAL(10, 2), nullable=True, comment='Average daily gain in kg'),
        sa.Column('weaning_date', sa.Date(), nullable=True, comment='Date of weaning'),
        sa.Column('sale_date', sa.Date(), nullable=True, comment='Date of sale if sold'),
        sa.Column('sale_price', sa.DECIMAL(10, 2), nullable=True, comment='Sale price if sold'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('enable', sa.Integer(), server_default='1', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['breeding_record_id'], ['breeding_records.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['livestock_id'], ['livestock.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['farmer_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('idx_offspring_breeding_record_id', 'offspring', ['breeding_record_id'])
    op.create_index('idx_offspring_livestock_id', 'offspring', ['livestock_id'])
    op.create_index('idx_offspring_farmer_id', 'offspring', ['farmer_id'])
    op.create_index('idx_offspring_birth_date', 'offspring', ['birth_date'])


def downgrade() -> None:
    """Drop breeding records and offspring tables"""
    op.drop_index('idx_offspring_birth_date', table_name='offspring')
    op.drop_index('idx_offspring_farmer_id', table_name='offspring')
    op.drop_index('idx_offspring_livestock_id', table_name='offspring')
    op.drop_index('idx_offspring_breeding_record_id', table_name='offspring')
    op.drop_table('offspring')
    
    op.drop_index('idx_breeding_records_pregnancy_status', table_name='breeding_records')
    op.drop_index('idx_breeding_records_breeding_date', table_name='breeding_records')
    op.drop_index('idx_breeding_records_farmer_id', table_name='breeding_records')
    op.drop_index('idx_breeding_records_livestock_id', table_name='breeding_records')
    op.drop_table('breeding_records')
