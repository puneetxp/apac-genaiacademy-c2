"""create supply_requests table

Revision ID: create_supply_requests
Revises: 02ce9fcea720
Create Date: 2026-03-10 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_supply_requests'
down_revision = '02ce9fcea720'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'supply_requests',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            onupdate=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),
        sa.Column('enable', sa.SmallInteger(), nullable=False, server_default='1'),
        sa.Column('buyer_id', sa.BigInteger(), nullable=False),
        sa.Column('crop_type', sa.String(length=100), nullable=False),
        sa.Column('quantity_needed', sa.Numeric(10, 2), nullable=False),
        sa.Column('quality_requirements', sa.Text(), nullable=True),
        sa.Column('delivery_date_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('delivery_date_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('max_price_per_unit', sa.Numeric(10, 2), nullable=True),
        sa.Column('recurring', sa.SmallInteger(), nullable=False, server_default='0'),
        sa.Column('recurrence_pattern', sa.Text(), nullable=True),
        sa.Column('is_emergency', sa.SmallInteger(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='open'),
        sa.Column('delivery_address', sa.Text(), nullable=True),
        sa.Column('delivery_latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('delivery_longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('delivery_pincode', sa.String(length=10), nullable=True),
        sa.Column('delivery_state', sa.String(length=100), nullable=True),
        sa.Column('delivery_district', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('active_role_id', sa.BigInteger(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('supply_requests')
