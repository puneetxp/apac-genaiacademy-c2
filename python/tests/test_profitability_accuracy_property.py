"""
Property-based tests for profitability calculation accuracy
Tests Property 20: Profitability Calculation Accuracy

**Validates: Requirements AC7 (Smart Land Plot Management)**
"""

from decimal import Decimal
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from app.services.plot_analysis_service import PlotAnalysisService


# Custom strategies for generating valid financial data
@st.composite
def crop_financial_data_strategy(draw):
    """
    Generate valid crop financial data for profitability testing

    This strategy creates realistic financial scenarios with:
    - Investment amounts (seeds, fertilizer, labor, irrigation)
    - Yield ranges (quintals per acre)
    - Market prices (per quintal)
    - Plot areas (acres)
    """

    # Generate investment per acre (₹5,000 to ₹50,000)
    investment_per_acre = draw(st.integers(min_value=5000, max_value=50000))

    # Generate yield range (15-40 quintals per acre)
    min_yield = draw(st.floats(min_value=15.0, max_value=30.0))
    max_yield = draw(st.floats(min_value=min_yield + 1.0, max_value=40.0))
    avg_yield = (min_yield + max_yield) / 2
    yield_str = f"{min_yield:.1f}-{max_yield:.1f} quintals"

    # Generate market price per quintal (₹1,500 to ₹5,000)
    market_price = draw(st.integers(min_value=1500, max_value=5000))

    # Generate plot area (0.5 to 100 acres)
    area = draw(st.floats(min_value=0.5, max_value=100.0))

    # Calculate expected values
    revenue_per_acre = avg_yield * market_price
    profit_per_acre = revenue_per_acre - investment_per_acre

    return {
        "investment_per_acre": investment_per_acre,
        "expected_yield_per_acre": yield_str,
        "average_yield": avg_yield,
        "market_price_per_quintal": market_price,
        "expected_revenue_per_acre": revenue_per_acre,
        "expected_profit_per_acre": profit_per_acre,
        "area": area,
        "crop_name": draw(st.sampled_from(["Rice", "Wheat", "Cotton", "Maize", "Soybean"])),
    }


@st.composite
def edge_case_financial_data_strategy(draw):
    """
    Generate edge case financial data including:
    - Zero investment scenarios
    - Very large numbers
    - Minimal profit margins
    - High ROI scenarios
    """

    scenario_type = draw(
        st.sampled_from(["zero_investment", "very_large_numbers", "minimal_profit", "high_roi"])
    )

    if scenario_type == "zero_investment":
        # Zero investment (should handle gracefully)
        investment = 0
        yield_val = draw(st.floats(min_value=15.0, max_value=30.0))
        price = draw(st.integers(min_value=1500, max_value=3000))
        area = draw(st.floats(min_value=1.0, max_value=10.0))

    elif scenario_type == "very_large_numbers":
        # Very large investment and area
        investment = draw(st.integers(min_value=100000, max_value=500000))
        yield_val = draw(st.floats(min_value=20.0, max_value=40.0))
        price = draw(st.integers(min_value=3000, max_value=10000))
        area = draw(st.floats(min_value=50.0, max_value=500.0))

    elif scenario_type == "minimal_profit":
        # Investment close to revenue (minimal profit margin)
        investment = draw(st.integers(min_value=20000, max_value=30000))
        yield_val = draw(st.floats(min_value=10.0, max_value=15.0))
        price = draw(st.integers(min_value=1500, max_value=2000))
        area = draw(st.floats(min_value=1.0, max_value=5.0))

    else:  # high_roi
        # Low investment, high yield (high ROI)
        investment = draw(st.integers(min_value=5000, max_value=10000))
        yield_val = draw(st.floats(min_value=30.0, max_value=40.0))
        price = draw(st.integers(min_value=3000, max_value=5000))
        area = draw(st.floats(min_value=1.0, max_value=10.0))

    revenue = yield_val * price
    profit = revenue - investment

    return {
        "investment_per_acre": investment,
        "expected_yield_per_acre": f"{yield_val:.1f} quintals",
        "average_yield": yield_val,
        "market_price_per_quintal": price,
        "expected_revenue_per_acre": revenue,
        "expected_profit_per_acre": profit,
        "area": area,
        "crop_name": "Test Crop",
        "scenario_type": scenario_type,
    }


class TestProfitabilityCalculationAccuracy:
    """
    Property 20: Profitability Calculation Accuracy

    Test that for any crop recommendation, profitability calculations are
    mathematically correct:
    - ROI = (profit / investment) * 100
    - Profit margin = (profit / revenue) * 100
    - Breakeven yield = investment / market_price
    - Profit = Revenue - Investment
    - Total metrics = Per-acre metrics * Area
    """

    @given(financial_data=crop_financial_data_strategy())
    @settings(
        max_examples=100,
        deadline=5000,  # 5 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_roi_calculation_accuracy(self, financial_data):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**

        Property: For any crop recommendation, ROI calculation must be
        mathematically accurate: ROI = (profit / investment) * 100
        """

        # Setup service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)

        # Create crop data
        crop = {
            "crop_name": financial_data["crop_name"],
            "investment_per_acre": financial_data["investment_per_acre"],
            "expected_yield_per_acre": financial_data["expected_yield_per_acre"],
            "market_price_per_quintal": financial_data["market_price_per_quintal"],
            "expected_revenue_per_acre": financial_data["expected_revenue_per_acre"],
            "expected_profit_per_acre": financial_data["expected_profit_per_acre"],
        }

        # Calculate profitability
        profitability = await service._calculate_profitability(
            crop=crop,
            area=financial_data["area"],
            budget_per_acre=financial_data["investment_per_acre"],
        )

        # Extract values
        investment = profitability["per_acre"]["investment"]
        profit = profitability["per_acre"]["profit"]
        roi = profitability["per_acre"]["roi_percentage"]

        # Calculate expected ROI
        if investment > 0:
            expected_roi = (profit / investment) * 100

            # Assert: ROI calculation is accurate (within 0.1% tolerance for floating point)
            assert abs(roi - expected_roi) < 0.1, (
                f"ROI calculation incorrect. Expected {expected_roi:.2f}%, got {roi:.2f}%. "
                f"Investment: ₹{investment}, Profit: ₹{profit}"
            )
        else:
            # Zero investment should result in 0 ROI
            assert roi == 0, f"ROI should be 0 for zero investment, got {roi:.2f}%"

    @given(financial_data=crop_financial_data_strategy())
    @settings(
        max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_profit_margin_calculation_accuracy(self, financial_data):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**

        Property: For any crop recommendation, profit margin calculation
        must be accurate: Profit Margin = (profit / revenue) * 100
        """

        # Setup service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)

        # Create crop data
        crop = {
            "crop_name": financial_data["crop_name"],
            "investment_per_acre": financial_data["investment_per_acre"],
            "expected_yield_per_acre": financial_data["expected_yield_per_acre"],
            "market_price_per_quintal": financial_data["market_price_per_quintal"],
        }

        # Calculate profitability
        profitability = await service._calculate_profitability(
            crop=crop,
            area=financial_data["area"],
            budget_per_acre=financial_data["investment_per_acre"],
        )

        # Extract values
        revenue = profitability["per_acre"]["revenue"]
        profit = profitability["per_acre"]["profit"]
        profit_margin = profitability["per_acre"]["profit_margin"]

        # Calculate expected profit margin
        if revenue > 0:
            expected_profit_margin = (profit / revenue) * 100

            # Assert: Profit margin calculation is accurate (within 0.1% tolerance)
            assert abs(profit_margin - expected_profit_margin) < 0.1, (
                f"Profit margin calculation incorrect. Expected {expected_profit_margin:.2f}%, got {profit_margin:.2f}%. "
                f"Revenue: ₹{revenue}, Profit: ₹{profit}"
            )
        else:
            # Zero revenue should result in 0 profit margin
            assert (
                profit_margin == 0
            ), f"Profit margin should be 0 for zero revenue, got {profit_margin:.2f}%"

    @given(financial_data=crop_financial_data_strategy())
    @settings(
        max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_breakeven_yield_calculation_accuracy(self, financial_data):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**

        Property: For any crop recommendation, breakeven yield calculation
        must be accurate: Breakeven Yield = investment / market_price
        """

        # Setup service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)

        # Create crop data
        crop = {
            "crop_name": financial_data["crop_name"],
            "investment_per_acre": financial_data["investment_per_acre"],
            "expected_yield_per_acre": financial_data["expected_yield_per_acre"],
            "market_price_per_quintal": financial_data["market_price_per_quintal"],
        }

        # Calculate profitability
        profitability = await service._calculate_profitability(
            crop=crop,
            area=financial_data["area"],
            budget_per_acre=financial_data["investment_per_acre"],
        )

        # Extract values
        investment = profitability["per_acre"]["investment"]
        market_price = profitability["per_acre"]["market_price"]
        breakeven_str = profitability["per_acre"]["breakeven_yield"]

        # Parse breakeven yield (e.g., "7.2 quintals" -> 7.2)
        breakeven_yield = float(breakeven_str.replace("quintals", "").strip())

        # Calculate expected breakeven yield
        if market_price > 0:
            expected_breakeven = investment / market_price

            # Assert: Breakeven yield calculation is accurate (within 0.1 quintal tolerance)
            assert abs(breakeven_yield - expected_breakeven) < 0.1, (
                f"Breakeven yield calculation incorrect. Expected {expected_breakeven:.1f} quintals, got {breakeven_yield:.1f} quintals. "
                f"Investment: ₹{investment}, Market Price: ₹{market_price}/quintal"
            )
        else:
            # Zero market price should result in 0 breakeven yield
            assert (
                breakeven_yield == 0
            ), f"Breakeven yield should be 0 for zero market price, got {breakeven_yield:.1f} quintals"

    @given(financial_data=crop_financial_data_strategy())
    @settings(
        max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_profit_calculation_accuracy(self, financial_data):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**

        Property: For any crop recommendation, profit calculation must be
        accurate: Profit = Revenue - Investment
        """

        # Setup service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)

        # Create crop data
        crop = {
            "crop_name": financial_data["crop_name"],
            "investment_per_acre": financial_data["investment_per_acre"],
            "expected_yield_per_acre": financial_data["expected_yield_per_acre"],
            "market_price_per_quintal": financial_data["market_price_per_quintal"],
        }

        # Calculate profitability
        profitability = await service._calculate_profitability(
            crop=crop,
            area=financial_data["area"],
            budget_per_acre=financial_data["investment_per_acre"],
        )

        # Extract values
        investment = profitability["per_acre"]["investment"]
        revenue = profitability["per_acre"]["revenue"]
        profit = profitability["per_acre"]["profit"]

        # Calculate expected profit
        expected_profit = revenue - investment

        # Assert: Profit calculation is accurate (within ₹1 tolerance for rounding)
        assert abs(profit - expected_profit) < 1.0, (
            f"Profit calculation incorrect. Expected ₹{expected_profit:.2f}, got ₹{profit:.2f}. "
            f"Revenue: ₹{revenue}, Investment: ₹{investment}"
        )

    @given(financial_data=crop_financial_data_strategy())
    @settings(
        max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_total_plot_calculations_accuracy(self, financial_data):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**

        Property: For any crop recommendation, total plot calculations must
        be accurate: Total = Per-Acre * Area
        """

        # Setup service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)

        # Create crop data
        crop = {
            "crop_name": financial_data["crop_name"],
            "investment_per_acre": financial_data["investment_per_acre"],
            "expected_yield_per_acre": financial_data["expected_yield_per_acre"],
            "market_price_per_quintal": financial_data["market_price_per_quintal"],
        }

        area = financial_data["area"]

        # Calculate profitability
        profitability = await service._calculate_profitability(
            crop=crop, area=area, budget_per_acre=financial_data["investment_per_acre"]
        )

        # Extract per-acre values
        per_acre_investment = profitability["per_acre"]["investment"]
        per_acre_revenue = profitability["per_acre"]["revenue"]
        per_acre_profit = profitability["per_acre"]["profit"]

        # Extract total plot values
        total_investment = profitability["total_plot"]["total_investment"]
        total_revenue = profitability["total_plot"]["total_revenue"]
        total_profit = profitability["total_plot"]["total_profit"]
        plot_area = profitability["total_plot"]["area_acres"]

        # Assert: Area is correct
        assert (
            abs(plot_area - area) < 0.01
        ), f"Plot area incorrect. Expected {area:.2f} acres, got {plot_area:.2f} acres"

        # Assert: Total investment = Per-acre investment * Area
        expected_total_investment = per_acre_investment * area
        assert abs(total_investment - expected_total_investment) < 10.0, (
            f"Total investment calculation incorrect. Expected ₹{expected_total_investment:.2f}, got ₹{total_investment:.2f}. "
            f"Per-acre: ₹{per_acre_investment}, Area: {area} acres"
        )

        # Assert: Total revenue = Per-acre revenue * Area
        expected_total_revenue = per_acre_revenue * area
        assert abs(total_revenue - expected_total_revenue) < 10.0, (
            f"Total revenue calculation incorrect. Expected ₹{expected_total_revenue:.2f}, got ₹{total_revenue:.2f}. "
            f"Per-acre: ₹{per_acre_revenue}, Area: {area} acres"
        )

        # Assert: Total profit = Per-acre profit * Area
        expected_total_profit = per_acre_profit * area
        assert abs(total_profit - expected_total_profit) < 10.0, (
            f"Total profit calculation incorrect. Expected ₹{expected_total_profit:.2f}, got ₹{total_profit:.2f}. "
            f"Per-acre: ₹{per_acre_profit}, Area: {area} acres"
        )

    @given(financial_data=crop_financial_data_strategy())
    @settings(
        max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_investment_breakdown_totals_to_investment(self, financial_data):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**

        Property: For any crop recommendation, investment breakdown
        components must sum to total investment.
        """

        # Setup service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)

        # Create crop data
        crop = {
            "crop_name": financial_data["crop_name"],
            "investment_per_acre": financial_data["investment_per_acre"],
            "expected_yield_per_acre": financial_data["expected_yield_per_acre"],
            "market_price_per_quintal": financial_data["market_price_per_quintal"],
        }

        # Calculate profitability
        profitability = await service._calculate_profitability(
            crop=crop,
            area=financial_data["area"],
            budget_per_acre=financial_data["investment_per_acre"],
        )

        # Extract values
        total_investment = profitability["per_acre"]["investment"]
        breakdown = profitability["investment_breakdown"]

        # Sum breakdown components
        breakdown_sum = (
            breakdown["seeds"]
            + breakdown["fertilizer"]
            + breakdown["labor"]
            + breakdown["irrigation"]
            + breakdown["other"]
        )

        # Assert: Breakdown sums to total investment (within ₹1 tolerance for rounding)
        assert abs(breakdown_sum - total_investment) < 1.0, (
            f"Investment breakdown does not sum to total investment. "
            f"Expected ₹{total_investment:.2f}, got ₹{breakdown_sum:.2f}. "
            f"Breakdown: Seeds ₹{breakdown['seeds']:.2f}, Fertilizer ₹{breakdown['fertilizer']:.2f}, "
            f"Labor ₹{breakdown['labor']:.2f}, Irrigation ₹{breakdown['irrigation']:.2f}, Other ₹{breakdown['other']:.2f}"
        )

    @given(financial_data=edge_case_financial_data_strategy())
    @settings(
        max_examples=50, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_edge_cases_handled_correctly(self, financial_data):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**

        Property: For edge cases (zero investment, very large numbers,
        minimal profit), calculations must handle gracefully without errors.
        """

        # Setup service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)

        # Create crop data
        crop = {
            "crop_name": financial_data["crop_name"],
            "investment_per_acre": financial_data["investment_per_acre"],
            "expected_yield_per_acre": financial_data["expected_yield_per_acre"],
            "market_price_per_quintal": financial_data["market_price_per_quintal"],
        }

        # Calculate profitability - should not raise exceptions
        try:
            profitability = await service._calculate_profitability(
                crop=crop,
                area=financial_data["area"],
                budget_per_acre=financial_data["investment_per_acre"],
            )

            # Assert: Result structure is valid
            assert "per_acre" in profitability, "per_acre missing from profitability"
            assert "total_plot" in profitability, "total_plot missing from profitability"
            assert (
                "investment_breakdown" in profitability
            ), "investment_breakdown missing from profitability"

            # Assert: All values are numeric
            assert isinstance(
                profitability["per_acre"]["investment"], (int, float)
            ), "Investment must be numeric"
            assert isinstance(
                profitability["per_acre"]["revenue"], (int, float)
            ), "Revenue must be numeric"
            assert isinstance(
                profitability["per_acre"]["profit"], (int, float)
            ), "Profit must be numeric"
            assert isinstance(
                profitability["per_acre"]["roi_percentage"], (int, float)
            ), "ROI must be numeric"

            # Assert: No NaN or Infinity values
            import math

            assert not math.isnan(
                profitability["per_acre"]["roi_percentage"]
            ), "ROI should not be NaN"
            assert not math.isinf(
                profitability["per_acre"]["roi_percentage"]
            ), "ROI should not be Infinity"

        except Exception as e:
            pytest.fail(
                f"Edge case handling failed for scenario '{financial_data.get('scenario_type', 'unknown')}': {str(e)}"
            )

    @given(financial_data=crop_financial_data_strategy())
    @settings(
        max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_all_profitability_fields_present(self, financial_data):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**

        Property: For any crop recommendation, profitability response must
        contain all required fields with valid data types.
        """

        # Setup service
        mock_db = AsyncMock()
        service = PlotAnalysisService(mock_db)

        # Create crop data
        crop = {
            "crop_name": financial_data["crop_name"],
            "investment_per_acre": financial_data["investment_per_acre"],
            "expected_yield_per_acre": financial_data["expected_yield_per_acre"],
            "market_price_per_quintal": financial_data["market_price_per_quintal"],
        }

        # Calculate profitability
        profitability = await service._calculate_profitability(
            crop=crop,
            area=financial_data["area"],
            budget_per_acre=financial_data["investment_per_acre"],
        )

        # Assert: Per-acre fields
        required_per_acre_fields = [
            "investment",
            "expected_yield",
            "average_yield",
            "market_price",
            "revenue",
            "profit",
            "roi_percentage",
            "profit_margin",
            "breakeven_yield",
        ]
        for field in required_per_acre_fields:
            assert (
                field in profitability["per_acre"]
            ), f"Required field '{field}' missing from per_acre profitability"

        # Assert: Total plot fields
        required_total_fields = [
            "area_acres",
            "total_investment",
            "total_yield",
            "total_revenue",
            "total_profit",
            "roi_percentage",
        ]
        for field in required_total_fields:
            assert (
                field in profitability["total_plot"]
            ), f"Required field '{field}' missing from total_plot profitability"

        # Assert: Investment breakdown fields
        required_breakdown_fields = ["seeds", "fertilizer", "labor", "irrigation", "other"]
        for field in required_breakdown_fields:
            assert (
                field in profitability["investment_breakdown"]
            ), f"Required field '{field}' missing from investment_breakdown"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
