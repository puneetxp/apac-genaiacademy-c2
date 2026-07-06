ALTER TABLE active_roles ADD CONSTRAINT active_role_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE active_roles ADD CONSTRAINT active_role_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE advance_bookings ADD CONSTRAINT advance_booking_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE advance_bookings ADD CONSTRAINT advance_booking_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE advance_bookings ADD CONSTRAINT advance_booking_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE ai_usage_quota ADD CONSTRAINT ai_usage_quota_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE annual_strategies ADD CONSTRAINT annual_strategy_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE annual_strategies ADD CONSTRAINT annual_strategy_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE buyer_interests ADD CONSTRAINT buyer_interest_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE crops ADD CONSTRAINT crop_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE crops ADD CONSTRAINT crop_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE crop_expenses ADD CONSTRAINT crop_expense_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE crop_milestones ADD CONSTRAINT crop_milestone_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE farms ADD CONSTRAINT farm_user_id_foreign FOREIGN KEY ("user_id") REFERENCES users ("id");
ALTER TABLE farms ADD CONSTRAINT farm_owner_id_foreign FOREIGN KEY ("owner_id") REFERENCES users ("id");

ALTER TABLE farm_plots ADD CONSTRAINT farm_plot_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE fertilizer_applications ADD CONSTRAINT fertilizer_application_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE fertilizer_applications ADD CONSTRAINT fertilizer_application_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE fertilizer_applications ADD CONSTRAINT fertilizer_application_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE fertilizer_applications ADD CONSTRAINT fertilizer_application_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE fertilizer_applications ADD CONSTRAINT fertilizer_application_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE livestock ADD CONSTRAINT livestock_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE livestock ADD CONSTRAINT livestock_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE livestock_health_records ADD CONSTRAINT livestock_health_record_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE livestock_listings ADD CONSTRAINT livestock_listing_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE livestock_listings ADD CONSTRAINT livestock_listing_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE livestock_marketplace_listings ADD CONSTRAINT livestock_marketplace_listing_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE livestock_marketplace_listings ADD CONSTRAINT livestock_marketplace_listing_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE livestock_transactions ADD CONSTRAINT livestock_transaction_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE livestock_transactions ADD CONSTRAINT livestock_transaction_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE livestock_transactions ADD CONSTRAINT livestock_transaction_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE market_prices ADD CONSTRAINT market_price_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE market_prices ADD CONSTRAINT market_price_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE market_prices ADD CONSTRAINT market_price_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE marketplace_listings ADD CONSTRAINT marketplace_listing_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE marketplace_listings ADD CONSTRAINT marketplace_listing_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE payment_milestones ADD CONSTRAINT payment_milestone_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE pest_disease_alerts ADD CONSTRAINT pest_disease_alert_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE pest_disease_alerts ADD CONSTRAINT pest_disease_alert_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE quality_verifications ADD CONSTRAINT quality_verification_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE soil_test_results ADD CONSTRAINT soil_test_result_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE soil_test_results ADD CONSTRAINT soil_test_result_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE supply_matches ADD CONSTRAINT supply_match_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE supply_matches ADD CONSTRAINT supply_match_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE supply_matches ADD CONSTRAINT supply_match_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE supply_requests ADD CONSTRAINT supply_request_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE transport_bookings ADD CONSTRAINT transport_booking_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE transport_bookings ADD CONSTRAINT transport_booking_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");
ALTER TABLE transport_bookings ADD CONSTRAINT transport_booking_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE transport_providers ADD CONSTRAINT transport_provider_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");

ALTER TABLE weather_alerts ADD CONSTRAINT weather_alert_active_role_id_foreign FOREIGN KEY ("active_role_id") REFERENCES active_roles ("id");