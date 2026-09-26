"""
Tests for Livestock Registration (Task 26.1)
Validates: Requirements AC11 (Phase 7 - Required)
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest


class TestLivestockSchemas:
    """Test livestock Pydantic schemas"""

    def test_livestock_create_schema_validation(self):
        """
        Test LivestockCreate schema validates correctly
        Validates: AC11 - System validates livestock data
        """
        from app.schemas.livestock import LivestockCreate

        # Valid data
        livestock_data = {
            "farm_id": 1,
            "farmer_id": 1,
            "species": "cattle",
            "breed": "Holstein",
            "quantity": 2,
            "purchase_price": Decimal("50000.00"),
            "purchase_date": date.today() - timedelta(days=365),
            "purpose": "dairy",
            "status": "active",
        }

        livestock = LivestockCreate(**livestock_data)

        assert livestock.species == "cattle"
        assert livestock.breed == "Holstein"
        assert livestock.quantity == 2
        assert livestock.purchase_price == Decimal("50000.00")
        assert livestock.purpose == "dairy"

    def test_livestock_schema_validates_species(self):
        """
        Test that invalid species are rejected
        Validates: AC11 - System validates livestock species
        """
        from pydantic import ValidationError

        from app.schemas.livestock import LivestockCreate

        livestock_data = {
            "farm_id": 1,
            "farmer_id": 1,
            "species": "invalid_species",
            "breed": "Test",
            "quantity": 1,
            "purchase_price": Decimal("10000.00"),
            "purchase_date": date.today(),
            "purpose": "dairy",
            "status": "active",
        }

        with pytest.raises(ValidationError) as exc_info:
            LivestockCreate(**livestock_data)

        assert "species" in str(exc_info.value).lower()

    def test_livestock_schema_validates_purpose(self):
        """
        Test that invalid purpose is rejected
        Validates: AC11 - System validates livestock purpose
        """
        from pydantic import ValidationError

        from app.schemas.livestock import LivestockCreate

        livestock_data = {
            "farm_id": 1,
            "farmer_id": 1,
            "species": "cattle",
            "breed": "Jersey",
            "quantity": 1,
            "purchase_price": Decimal("40000.00"),
            "purchase_date": date.today(),
            "purpose": "invalid_purpose",
            "status": "active",
        }

        with pytest.raises(ValidationError) as exc_info:
            LivestockCreate(**livestock_data)

        assert "purpose" in str(exc_info.value).lower()


class TestLivestockROICalculations:
    """Test ROI calculation accuracy"""

    def test_dairy_cattle_roi_calculation(self):
        """
        Test ROI calculation for dairy cattle
        Validates: AC11 - System calculates ROI based on breed characteristics
        """
        from app.services.livestock_roi_service import get_roi_calculator

        roi_calculator = get_roi_calculator()

        roi_metrics = roi_calculator.calculate_roi(
            species="cattle",
            purpose="dairy",
            purchase_price=50000.00,
            current_age_months=24,  # 2 years old
            total_investment=50000.00,
            total_revenue=0.0,
            milk_production_liters_per_day=None,
        )

        # Verify ROI metrics are calculated
        assert "current_roi_percentage" in roi_metrics
        assert "net_profit" in roi_metrics
        assert "break_even_date" in roi_metrics
        assert "projected_annual_profit" in roi_metrics
        assert "monthly_costs" in roi_metrics
        assert "monthly_revenue" in roi_metrics

        # Dairy cattle should have positive monthly revenue
        assert roi_metrics["monthly_revenue"] > 0
        assert roi_metrics["monthly_costs"] > 0

        # For dairy cattle, revenue should exceed costs
        assert roi_metrics["monthly_revenue"] > roi_metrics["monthly_costs"]

    def test_meat_goat_roi_calculation(self):
        """
        Test ROI calculation for meat goats
        Validates: AC11 - System provides purpose-specific ROI calculations
        """
        from app.services.livestock_roi_service import get_roi_calculator

        roi_calculator = get_roi_calculator()

        roi_metrics = roi_calculator.calculate_roi(
            species="goat",
            purpose="meat",
            purchase_price=15000.00,
            current_age_months=6,
            total_investment=15000.00,
            total_revenue=0.0,
            milk_production_liters_per_day=None,
        )

        # Verify ROI metrics
        assert roi_metrics["monthly_costs"] > 0
        assert roi_metrics["projected_annual_profit"] is not None

        # Goats should have lower costs than cattle
        assert roi_metrics["monthly_costs"] < 4000  # Less than cattle

    def test_poultry_eggs_roi_calculation(self):
        """
        Test ROI calculation for egg-laying poultry
        Validates: AC11 - System handles different livestock types
        """
        from app.services.livestock_roi_service import get_roi_calculator

        roi_calculator = get_roi_calculator()

        roi_metrics = roi_calculator.calculate_roi(
            species="poultry",
            purpose="eggs",
            purchase_price=10000.00,
            current_age_months=3,
            total_investment=10000.00,
            total_revenue=0.0,
            milk_production_liters_per_day=None,
        )

        # Poultry should have much lower costs
        assert roi_metrics["monthly_costs"] < 100  # Very low per bird
        assert roi_metrics["monthly_revenue"] > 0

    def test_break_even_calculation(self):
        """
        Test break-even date calculation
        Validates: AC11 - System calculates expected break-even timeline within 30 days accuracy
        """
        from app.services.livestock_roi_service import get_roi_calculator

        roi_calculator = get_roi_calculator()

        roi_metrics = roi_calculator.calculate_roi(
            species="buffalo",
            purpose="dairy",
            purchase_price=60000.00,
            current_age_months=36,  # 3 years old, mature
            total_investment=60000.00,
            total_revenue=0.0,
            milk_production_liters_per_day=None,
        )

        # Break-even date should be calculated
        assert roi_metrics["break_even_date"] is not None

        # Payback period should be reasonable (not None for positive cash flow)
        if roi_metrics["monthly_cash_flow"] > 0:
            assert roi_metrics["payback_period_months"] is not None
            assert roi_metrics["payback_period_months"] > 0

    def test_roi_report_generation(self):
        """
        Test comprehensive ROI report generation
        Validates: AC11 - System generates detailed ROI analysis
        """
        from app.services.livestock_roi_service import get_roi_calculator

        roi_calculator = get_roi_calculator()

        livestock_data = {
            "species": "cattle",
            "breed": "Gir",
            "purpose": "dairy",
            "purchase_price": 45000.00,
            "current_age_months": 24,
        }

        roi_metrics = roi_calculator.calculate_roi(
            species="cattle",
            purpose="dairy",
            purchase_price=45000.00,
            current_age_months=24,
            total_investment=45000.00,
            total_revenue=0.0,
            milk_production_liters_per_day=None,
        )

        report = roi_calculator.generate_roi_report(livestock_data, roi_metrics)

        # Verify report structure
        assert "livestock_info" in report
        assert "financial_summary" in report
        assert "break_even_analysis" in report
        assert "cash_flow" in report
        assert "projected_returns" in report  # Updated field name
        assert "investment_vs_return" in report  # New field
        assert "recommendations" in report

        # Verify recommendations are provided
        assert len(report["recommendations"]) > 0

    def test_monthly_costs_by_species(self):
        """
        Test that monthly costs vary appropriately by species
        Validates: AC11 - System uses species-specific cost models
        """
        from app.services.livestock_roi_service import get_roi_calculator

        roi_calculator = get_roi_calculator()

        # Calculate costs for different species
        cattle_roi = roi_calculator.calculate_roi(
            species="cattle",
            purpose="dairy",
            purchase_price=50000.00,
            current_age_months=24,
            total_investment=50000.00,
            total_revenue=0.0,
        )

        goat_roi = roi_calculator.calculate_roi(
            species="goat",
            purpose="meat",
            purchase_price=15000.00,
            current_age_months=12,
            total_investment=15000.00,
            total_revenue=0.0,
        )

        poultry_roi = roi_calculator.calculate_roi(
            species="poultry",
            purpose="eggs",
            purchase_price=100.00,
            current_age_months=3,
            total_investment=100.00,
            total_revenue=0.0,
        )

        # Verify cost hierarchy: cattle > goat > poultry
        assert cattle_roi["monthly_costs"] > goat_roi["monthly_costs"]
        assert goat_roi["monthly_costs"] > poultry_roi["monthly_costs"]


class TestLivestockService:
    """Test livestock service operations"""

    def test_livestock_roi_calculator_singleton(self):
        """
        Test ROI calculator singleton pattern
        Validates: AC11 - System provides consistent ROI calculations
        """
        from app.services.livestock_roi_service import get_roi_calculator

        calculator1 = get_roi_calculator()
        calculator2 = get_roi_calculator()

        # Should return same instance
        assert calculator1 is calculator2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
