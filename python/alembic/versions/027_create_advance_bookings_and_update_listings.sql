-- Migration: Create advance_bookings table and add available_quantity to listings
-- Revision: 027
-- Date: 2026-03-01

-- Add available_quantity to listings table
ALTER TABLE listings 
ADD COLUMN IF NOT EXISTS available_quantity NUMERIC(10,2) NULL 
COMMENT 'Available quantity for booking (defaults to estimated_quantity)';

-- Set available_quantity to estimated_quantity for existing records
UPDATE listings 
SET available_quantity = estimated_quantity 
WHERE available_quantity IS NULL;

-- Create advance_bookings table
CREATE TABLE IF NOT EXISTS advance_bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    buyer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farmer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quantity_booked NUMERIC(10,2) NOT NULL,
    price_per_unit NUMERIC(10,2) NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    advance_payment_percent INT NOT NULL DEFAULT 20 CHECK (advance_payment_percent >= 20 AND advance_payment_percent <= 50),
    advance_payment_amount NUMERIC(10,2) NOT NULL,
    booking_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expected_delivery_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'quality_check', 'delivered', 'cancelled')),
    quality_standards JSONB NULL,
    contract_terms JSONB NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for advance_bookings
CREATE INDEX IF NOT EXISTS idx_advance_bookings_listing_id ON advance_bookings(listing_id);
CREATE INDEX IF NOT EXISTS idx_advance_bookings_buyer_id ON advance_bookings(buyer_id);
CREATE INDEX IF NOT EXISTS idx_advance_bookings_farmer_id ON advance_bookings(farmer_id);
CREATE INDEX IF NOT EXISTS idx_advance_bookings_status ON advance_bookings(status);
CREATE INDEX IF NOT EXISTS idx_advance_bookings_expected_delivery_date ON advance_bookings(expected_delivery_date);

-- Create quality_verifications table
CREATE TABLE IF NOT EXISTS quality_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES advance_bookings(id) ON DELETE CASCADE,
    verification_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    verifier_type VARCHAR(50) NOT NULL CHECK (verifier_type IN ('platform', 'third_party', 'buyer')),
    quality_grade VARCHAR(10) NOT NULL,
    quality_metrics JSONB NULL,
    photos JSONB NULL,
    passed BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for quality_verifications
CREATE INDEX IF NOT EXISTS idx_quality_verifications_booking_id ON quality_verifications(booking_id);
CREATE INDEX IF NOT EXISTS idx_quality_verifications_verification_date ON quality_verifications(verification_date);

-- Create payment_milestones table
CREATE TABLE IF NOT EXISTS payment_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES advance_bookings(id) ON DELETE CASCADE,
    milestone_type VARCHAR(50) NOT NULL CHECK (milestone_type IN ('advance', 'quality_check', 'delivery', 'final')),
    amount NUMERIC(10,2) NOT NULL,
    due_date DATE NOT NULL,
    paid_date TIMESTAMP WITH TIME ZONE NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'due', 'paid', 'overdue')),
    payment_method VARCHAR(50) NULL,
    transaction_id VARCHAR(255) NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for payment_milestones
CREATE INDEX IF NOT EXISTS idx_payment_milestones_booking_id ON payment_milestones(booking_id);
CREATE INDEX IF NOT EXISTS idx_payment_milestones_status ON payment_milestones(status);
CREATE INDEX IF NOT EXISTS idx_payment_milestones_due_date ON payment_milestones(due_date);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_advance_bookings_updated_at BEFORE UPDATE ON advance_bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE advance_bookings IS 'Pre-harvest advance bookings with quality standards and payment milestones';
COMMENT ON TABLE quality_verifications IS 'Quality verification records for advance bookings';
COMMENT ON TABLE payment_milestones IS 'Payment milestone tracking for advance bookings';
