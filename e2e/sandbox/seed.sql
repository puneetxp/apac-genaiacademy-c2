-- Seed data for the throwaway E2E database (cropsense_e2e). Loaded by reset-db.sh after the schema.
-- Every seeded user signs in with the backend's E2E_PASSWORD (default "E2e-Test-Pass1!").
-- Fixed ids keep specs deterministic; sequences are bumped at the end so app inserts don't collide.

BEGIN;

INSERT INTO roles (id, name) VALUES (1, 'isuper');

INSERT INTO users (id, cognito_user_id, firebase_id, username, name, email, phone, user_type,
                   state, district, village, pincode, latitude, longitude, is_active, is_verified)
VALUES
  (1, 'e2e-farmer-uid', 'e2e-farmer-uid', 'e2e_farmer', 'E2E Farmer', 'e2e.farmer@example.com', '+919000000001', 'farmer',
   'Maharashtra', 'Pune', 'Wagholi', '412207', 18.58000000, 73.97000000, 1, 1),
  (2, 'e2e-buyer-uid', 'e2e-buyer-uid', 'e2e_buyer', 'E2E Buyer', 'e2e.buyer@example.com', '+919000000002', 'buyer',
   'Maharashtra', 'Mumbai', NULL, '400001', 18.94000000, 72.83000000, 1, 1),
  (3, 'e2e-admin-uid', 'e2e-admin-uid', 'e2e_admin', 'E2E Admin', 'e2e.admin@example.com', '+919000000003', 'admin',
   'Delhi', 'New Delhi', NULL, '110001', 28.61000000, 77.21000000, 1, 1);

INSERT INTO active_roles (user_id, role_id) VALUES (1, 1);

INSERT INTO farms (id, name, description, location_state, location_district, location_village, latitude, longitude,
                   total_area, cultivable_area, area_unit, primary_soil_type, soil_ph, irrigation_type,
                   water_availability, farming_experience_years, investment_capacity_per_acre, user_id, owner_id)
VALUES (1, 'E2E Green Acres', 'Seeded farm for end-to-end tests', 'Maharashtra', 'Pune', 'Wagholi', 18.58000000, 73.97000000,
        10.00, 8.00, 'acres', 'black', 7.2, 'drip', 'medium', 12, 25000.00, 1, 1);

INSERT INTO farm_plots (id, farm_id, plot_name, area, soil_type, irrigation_type, state, district,
                        nitrogen, phosphorus, potassium, ph_level, organic_carbon)
VALUES (1, 1, 'North Plot', 4.00, 'black', 'drip', 'Maharashtra', 'Pune', 280.00, 22.00, 310.00, 7.20, 0.65),
       (2, 1, 'South Plot', 4.00, 'loamy', 'canal', 'Maharashtra', 'Pune', 240.00, 18.00, 260.00, 6.80, 0.55);

INSERT INTO crops (id, farm_plot_id, crop_name, crop_variety, season, planting_date, expected_harvest_date,
                   area, expected_yield, expected_profit, status)
VALUES (1, 1, 'Soybean', 'JS 335', 'kharif', CURRENT_DATE - 40, CURRENT_DATE + 60, 4.00, 4800.00, 90000.00, 'growing');

INSERT INTO crop_expenses (crop_id, category, amount, description, expense_date)
VALUES (1, 'seeds', 6500.00, 'Certified soybean seed', CURRENT_DATE - 41),
       (1, 'fertilizer', 4200.00, 'DAP basal dose', CURRENT_DATE - 38);

INSERT INTO marketplace_listings (id, farm_id, farmer_id, crop_type, crop_variety, expected_harvest_date,
                                  estimated_quantity, available_quantity, quality_grade, location_state,
                                  location_district, farmer_contact_phone, farmer_contact_email, status, price_per_unit)
VALUES (1, 1, 1, 'Soybean', 'JS 335', CURRENT_DATE + 60, 4800, 4800, 'A', 'Maharashtra', 'Pune',
        '+919000000001', 'e2e.farmer@example.com', 'active', 48.50);

INSERT INTO livestock (id, farm_id, farmer_id, species, breed, quantity, purchase_price, purchase_date, purpose,
                       status, state, district, village, pincode)
VALUES (1, 1, 1, 'cattle', 'Gir', 3, 150000.00, CURRENT_DATE - 365, 'dairy', 'active', 'Maharashtra', 'Pune', 'Wagholi', '412207'),
       (2, 1, 1, 'goat', 'Osmanabadi', 10, 60000.00, CURRENT_DATE - 200, 'meat', 'active', 'Maharashtra', 'Pune', 'Wagholi', '412207');

INSERT INTO livestock_health_records (livestock_id, record_type, record_date, description, veterinarian_name, cost, next_due_date)
VALUES (1, 'vaccination', CURRENT_DATE - 150, 'FMD vaccination', 'Dr. E2E Vet', 300.00, CURRENT_DATE + 30);

INSERT INTO livestock_listings (id, livestock_id, farmer_id, title, description, species, breed, age_years, gender,
                                quantity, purpose, price, weight_kg, health_status, vaccination_status,
                                location_state, location_district, location_village, farmer_contact_phone, status)
VALUES (1, 2, 1, 'Osmanabadi goats for sale', 'Healthy, vaccinated', 'goat', 'Osmanabadi', 2, 'female',
        5, 'meat', 12000.00, 32.00, 'healthy', 'up_to_date', 'Maharashtra', 'Pune', 'Wagholi', '+919000000001', 'active');

INSERT INTO veterinarians (name, clinic_name, specialization, species_supported, phone, whatsapp, email,
                           location_state, location_district, address, available_now, verified, rating, total_ratings)
VALUES ('Dr. E2E Vet', 'Pune Animal Care', 'large_animal', '["cattle","buffalo","goat"]', '+919000000010', '+919000000010',
        'vet@example.com', 'Maharashtra', 'Pune', 'Wagholi Road', 1, 1, 4.60, 12),
       ('Dr. Test Poultry', 'Mumbai Poultry Clinic', 'poultry', '["poultry"]', '+919000000011', NULL,
        NULL, 'Maharashtra', 'Mumbai', 'Andheri', 0, 1, 4.20, 5);

INSERT INTO msp_rates (crop_name, year, season, msp_per_quintal, msp_per_kg, source)
VALUES ('Soybean', EXTRACT(YEAR FROM CURRENT_DATE)::int, 'kharif', 4892.00, 48.92, 'e2e-seed'),
       ('Wheat', EXTRACT(YEAR FROM CURRENT_DATE)::int, 'rabi', 2425.00, 24.25, 'e2e-seed');

INSERT INTO crop_market_data (crop_name, state, district, price_per_kg, date, season, yoy_growth, demand_level)
VALUES ('Soybean', 'Maharashtra', 'Pune', 47.80, CURRENT_DATE - 7, 'kharif', 6.5, 'high'),
       ('Soybean', 'Maharashtra', 'Pune', 48.40, CURRENT_DATE - 1, 'kharif', 6.9, 'high');

COMMIT;

-- Move every id sequence past the seeded rows.
DO $$
DECLARE r record;
BEGIN
  FOR r IN SELECT c.table_name FROM information_schema.columns c
           WHERE c.table_schema = 'public' AND c.column_name = 'id' AND c.column_default LIKE 'nextval%'
  LOOP
    EXECUTE format('SELECT setval(pg_get_serial_sequence(%L, ''id''), GREATEST((SELECT COALESCE(MAX(id), 0) FROM %I), 1000))',
                   r.table_name, r.table_name);
  END LOOP;
END $$;
