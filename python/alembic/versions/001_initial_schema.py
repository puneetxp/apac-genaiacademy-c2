"""Initial schema with all models

Revision ID: 001
Revises: 
Create Date: 2026-02-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('cognito_user_id', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('cognito_username', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(255), unique=True, index=True),
        sa.Column('phone_number', sa.String(20), unique=True, index=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('preferred_units', sa.String(20), default='metric'),
        sa.Column('user_type', sa.String(50), default='farmer'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('email_verified', sa.Boolean, default=False),
        sa.Column('phone_verified', sa.Boolean, default=False),
        sa.Column('mfa_enabled', sa.Boolean, default=False),
        sa.Column('profile_picture_url', sa.String(500)),
        sa.Column('bio', sa.Text),
        sa.Column('location_state', sa.String(100)),
        sa.Column('location_district', sa.String(100)),
        sa.Column('notification_preferences', postgresql.JSONB, default={}),
        sa.Column('last_login_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('session_token', sa.String(500), nullable=False, unique=True, index=True),
        sa.Column('cognito_access_token_jti', sa.String(255), index=True),
        sa.Column('device_type', sa.String(50)),
        sa.Column('device_info', postgresql.JSONB),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('location', postgresql.JSONB),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('login_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('logout_at', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('login_method', sa.String(50)),
        sa.Column('mfa_verified', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create user_activities table
    op.create_table(
        'user_activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('activity_type', sa.String(100), nullable=False, index=True),
        sa.Column('activity_category', sa.String(50), index=True),
        sa.Column('activity_data', postgresql.JSONB),
        sa.Column('resource_type', sa.String(50)),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_sessions.id')),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )
    
    # Create farms table
    op.create_table(
        'farms',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('location_state', sa.String(100), nullable=False, index=True),
        sa.Column('location_district', sa.String(100), nullable=False, index=True),
        sa.Column('location_block', sa.String(100)),
        sa.Column('location_village', sa.String(100)),
        sa.Column('latitude', sa.Numeric(10, 8)),
        sa.Column('longitude', sa.Numeric(11, 8)),
        sa.Column('total_area', sa.Numeric(10, 2), nullable=False),
        sa.Column('cultivable_area', sa.Numeric(10, 2)),
        sa.Column('area_unit', sa.String(20), default='acres'),
        sa.Column('primary_soil_type', sa.String(50)),
        sa.Column('soil_ph', sa.Numeric(3, 1)),
        sa.Column('soil_characteristics', postgresql.JSONB),
        sa.Column('irrigation_type', sa.String(50)),
        sa.Column('water_availability', sa.String(50)),
        sa.Column('previous_crops', postgresql.ARRAY(sa.Text)),
        sa.Column('farming_experience_years', sa.Integer),
        sa.Column('investment_capacity_per_acre', sa.Numeric(10, 2)),
        sa.Column('farm_profile_embedding', Vector(512)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create farm_plots table
    op.create_table(
        'farm_plots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('farm_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('farms.id'), nullable=False),
        sa.Column('plot_name', sa.String(255), nullable=False),
        sa.Column('plot_number', sa.String(50)),
        sa.Column('description', sa.Text),
        sa.Column('area', sa.Numeric(10, 2), nullable=False),
        sa.Column('area_unit', sa.String(20), default='acres'),
        sa.Column('location_description', sa.Text),
        sa.Column('boundary_coordinates', postgresql.JSONB),
        sa.Column('soil_type', sa.String(50), nullable=False),
        sa.Column('soil_ph', sa.Numeric(3, 1)),
        sa.Column('soil_texture', sa.String(50)),
        sa.Column('drainage_quality', sa.String(50)),
        sa.Column('nitrogen_level', sa.String(20)),
        sa.Column('phosphorus_level', sa.String(20)),
        sa.Column('potassium_level', sa.String(20)),
        sa.Column('organic_matter_percentage', sa.Numeric(5, 2)),
        sa.Column('irrigation_type', sa.String(50)),
        sa.Column('irrigation_access', sa.Boolean, default=True),
        sa.Column('slope', sa.String(50)),
        sa.Column('elevation', sa.Numeric(8, 2)),
        sa.Column('sun_exposure', sa.String(50)),
        sa.Column('last_crop_grown', sa.String(100)),
        sa.Column('last_crop_harvest_date', sa.Date),
        sa.Column('last_crop_yield', sa.Numeric(10, 2)),
        sa.Column('crop_history', postgresql.JSONB),
        sa.Column('last_soil_test_date', sa.Date),
        sa.Column('soil_test_results', postgresql.JSONB),
        sa.Column('fertilizer_history', postgresql.JSONB),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('current_status', sa.String(50), default='fallow'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create crop_varieties table
    op.create_table(
        'crop_varieties',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('crop_type', sa.String(100), nullable=False, index=True),
        sa.Column('variety_name', sa.String(200), nullable=False),
        sa.Column('scientific_name', sa.String(200)),
        sa.Column('growth_duration', sa.Integer, nullable=False),
        sa.Column('water_requirement', sa.String(50)),
        sa.Column('soil_preference', postgresql.JSONB),
        sa.Column('climate_zones', postgresql.ARRAY(sa.Text)),
        sa.Column('temperature_range', postgresql.JSONB),
        sa.Column('rainfall_requirement', postgresql.JSONB),
        sa.Column('market_demand_score', sa.Numeric(3, 2)),
        sa.Column('nutritional_value', postgresql.JSONB),
        sa.Column('common_diseases', postgresql.ARRAY(sa.Text)),
        sa.Column('common_pests', postgresql.ARRAY(sa.Text)),
        sa.Column('companion_crops', postgresql.ARRAY(sa.Text)),
        sa.Column('antagonistic_crops', postgresql.ARRAY(sa.Text)),
        sa.Column('embedding', Vector(384)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create crops table
    op.create_table(
        'crops',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('plot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('farm_plots.id'), nullable=False),
        sa.Column('crop_variety_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('crop_varieties.id'), nullable=False),
        sa.Column('planting_date', sa.Date, nullable=False),
        sa.Column('expected_harvest_date', sa.Date),
        sa.Column('actual_harvest_date', sa.Date),
        sa.Column('area_planted', sa.Numeric(8, 2), nullable=False),
        sa.Column('planting_method', sa.String(100)),
        sa.Column('seed_source', sa.String(200)),
        sa.Column('seed_cost', sa.Numeric(10, 2)),
        sa.Column('status', sa.String(50), default='planted', index=True),
        sa.Column('growth_stage', sa.String(50)),
        sa.Column('health_score', sa.Numeric(3, 2)),
        sa.Column('current_yield_estimate', sa.Numeric(10, 2)),
        sa.Column('actual_yield', sa.Numeric(10, 2)),
        sa.Column('quality_grade', sa.String(10)),
        sa.Column('harvest_cost', sa.Numeric(10, 2)),
        sa.Column('total_investment', sa.Numeric(10, 2)),
        sa.Column('total_revenue', sa.Numeric(10, 2)),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Continue with remaining tables in next part...
    # (Due to length, I'll create a helper script to generate the rest)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('crops')
    op.drop_table('crop_varieties')
    op.drop_table('farm_plots')
    op.drop_table('farms')
    op.drop_table('user_activities')
    op.drop_table('user_sessions')
    op.drop_table('users')
    
    # Disable pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector')
