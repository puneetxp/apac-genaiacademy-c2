"""create marketplace_listings table

Revision ID: create_marketplace_listings
Revises: create_supply_requests
Create Date: 2026-03-10 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_marketplace_listings'
down_revision = 'create_supply_requests'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'marketplace_listings',
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
        sa.Column('farm_id', sa.BigInteger(), nullable=False),
        sa.Column('farmer_id', sa.BigInteger(), nullable=False),
        sa.Column('crop_type', sa.String(length=255), nullable=False),
        sa.Column('crop_variety', sa.String(length=255), nullable=True),
        sa.Column('expected_harvest_date', sa.Date(), nullable=False),
        sa.Column('estimated_quantity', sa.Integer(), nullable=False, comment='Quantity in kg'),
        sa.Column('available_quantity', sa.Integer(), nullable=True, comment='Available quantity defaults to estimated_quantity'),
        sa.Column('quality_grade', sa.String(length=255), nullable=True, comment='A, B, C grade prediction'),
        sa.Column('location_state', sa.String(length=255), nullable=False),
        sa.Column('location_district', sa.String(length=255), nullable=False),
        sa.Column('farmer_contact_phone', sa.String(length=255), nullable=True),
        sa.Column('farmer_contact_email', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=255), server_default='active', nullable=False, comment='active, booked, harvested, cancelled'),
        sa.Column('delivery_latitude', sa.Numeric(10, 8), nullable=True, comment='Delivery location GPS latitude (optional)'),
        sa.Column('delivery_longitude', sa.Numeric(11, 8), nullable=True, comment='Delivery location GPS longitude (optional)'),
        sa.Column('delivery_pincode', sa.String(length=10), nullable=True, comment='Delivery location postal code'),
        sa.Column('delivery_village', sa.String(length=100), nullable=True, comment='Delivery location village/VPO'),
        sa.Column('delivery_address_line', sa.String(length=255), nullable=True, comment='Full delivery address'),
        sa.Column('price_per_unit', sa.Numeric(10, 2), nullable=True, comment='Price per kg in INR'),
        sa.Column('active_role_id', sa.BigInteger(), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('marketplace_listings')
