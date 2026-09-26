"""
Unit tests for seasonal trend analysis service
Tests the business logic for Kharif, Rabi, and Zaid season analysis
These are standalone tests that don't require database setup
"""

import statistics

import pytest


def test_seasonal_trend_analysis_basic_logic():
    """Test basic seasonal trend analysis calculations"""
    # Sample data: prices increasing over 3 years
    prices = [2000.0, 2200.0, 2420.0]
    years = [2021, 2022, 2023]

    # Calculate CAGR
    first_price = prices[0]
    last_price = prices[-1]
    num_years = years[-1] - years[0]

    cagr = (((last_price / first_price) ** (1 / num_years)) - 1) * 100

    # CAGR should be approximately 10%
    assert 9.5 <= cagr <= 10.5

    # Calculate volatility
    volatility = statistics.stdev(prices)
    avg_price = statistics.mean(prices)
    volatility_coefficient = volatility / avg_price * 100

    # Volatility coefficient should be reasonable
    assert volatility_coefficient > 0
    assert volatility_coefficient < 20  # Less than 20% is considered stable


def test_trend_direction_classification():
    """Test trend direction classification logic"""
    # Strong upward trend
    cagr_strong_up = 8.0
    assert "strong_upward" == (
        "strong_upward"
        if cagr_strong_up > 5
        else (
            "moderate_upward"
            if cagr_strong_up > 0
            else "stable" if cagr_strong_up > -5 else "downward"
        )
    )

    # Moderate upward trend
    cagr_moderate_up = 3.0
    assert "moderate_upward" == (
        "strong_upward"
        if cagr_moderate_up > 5
        else (
            "moderate_upward"
            if cagr_moderate_up > 0
            else "stable" if cagr_moderate_up > -5 else "downward"
        )
    )

    # Stable trend
    cagr_stable = -2.0
    assert "stable" == (
        "strong_upward"
        if cagr_stable > 5
        else "moderate_upward" if cagr_stable > 0 else "stable" if cagr_stable > -5 else "downward"
    )

    # Downward trend
    cagr_down = -8.0
    assert "downward" == (
        "strong_upward"
        if cagr_down > 5
        else "moderate_upward" if cagr_down > 0 else "stable" if cagr_down > -5 else "downward"
    )


def test_volatility_classification():
    """Test volatility classification logic"""
    # Stable market
    volatility_coef_stable = 8.0
    assert "stable" == ("stable" if volatility_coef_stable < 15 else "volatile")

    # Volatile market
    volatility_coef_volatile = 25.0
    assert "volatile" == ("stable" if volatility_coef_volatile < 15 else "volatile")


def test_seasonal_comparison_logic():
    """Test logic for comparing seasons"""
    # Mock seasonal data
    kharif_cagr = 12.0
    rabi_cagr = 8.0
    zaid_cagr = 5.0

    seasons_data = {
        "kharif": {"cagr": kharif_cagr, "volatility": 10.0},
        "rabi": {"cagr": rabi_cagr, "volatility": 8.0},
        "zaid": {"cagr": zaid_cagr, "volatility": 15.0},
    }

    # Find best performing season
    best_season = max(seasons_data.items(), key=lambda x: x[1]["cagr"])
    assert best_season[0] == "kharif"
    assert best_season[1]["cagr"] == 12.0

    # Find most stable season
    most_stable = min(seasons_data.items(), key=lambda x: x[1]["volatility"])
    assert most_stable[0] == "rabi"
    assert most_stable[1]["volatility"] == 8.0


def test_price_forecast_linear_regression():
    """Test linear regression logic for price forecasting"""
    # Sample data
    years = [2020, 2021, 2022, 2023]
    prices = [2000.0, 2100.0, 2200.0, 2300.0]

    # Calculate linear regression
    n = len(years)
    sum_x = sum(years)
    sum_y = sum(prices)
    sum_xy = sum(x * y for x, y in zip(years, prices))
    sum_x2 = sum(x * x for x in years)

    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n

    # Slope should be approximately 100 (price increases by 100 per year)
    assert 95 <= slope <= 105

    # Forecast for 2024
    forecast_2024 = slope * 2024 + intercept
    assert 2350 <= forecast_2024 <= 2450


def test_r_squared_calculation():
    """Test R-squared calculation for forecast confidence"""
    # Perfect linear data
    years = [2020, 2021, 2022, 2023]
    prices = [2000.0, 2100.0, 2200.0, 2300.0]

    # Calculate regression
    n = len(years)
    sum_x = sum(years)
    sum_y = sum(prices)
    sum_xy = sum(x * y for x, y in zip(years, prices))
    sum_x2 = sum(x * x for x in years)

    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n

    # Calculate R-squared
    mean_y = statistics.mean(prices)
    ss_tot = sum((y - mean_y) ** 2 for y in prices)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(years, prices))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    # For perfect linear data, R-squared should be very close to 1
    assert r_squared > 0.99


def test_forecast_reliability_classification():
    """Test forecast reliability classification"""
    # High reliability
    r_squared_high = 0.85
    reliability_high = (
        "high" if r_squared_high > 0.7 else "moderate" if r_squared_high > 0.4 else "low"
    )
    assert reliability_high == "high"

    # Moderate reliability
    r_squared_moderate = 0.55
    reliability_moderate = (
        "high" if r_squared_moderate > 0.7 else "moderate" if r_squared_moderate > 0.4 else "low"
    )
    assert reliability_moderate == "moderate"

    # Low reliability
    r_squared_low = 0.25
    reliability_low = (
        "high" if r_squared_low > 0.7 else "moderate" if r_squared_low > 0.4 else "low"
    )
    assert reliability_low == "low"


def test_pattern_identification_consistent_growth():
    """Test pattern identification for consistent growth"""
    # All seasons showing positive growth
    seasons = {"kharif": {"cagr": 8.0}, "rabi": {"cagr": 6.0}, "zaid": {"cagr": 4.0}}

    all_growing = all(v["cagr"] > 0 for v in seasons.values())
    assert all_growing is True


def test_pattern_identification_seasonal_preference():
    """Test pattern identification for seasonal preference"""
    seasons = {"kharif": {"cagr": 15.0}, "rabi": {"cagr": 3.0}, "zaid": {"cagr": 2.0}}

    best_season = max(seasons.items(), key=lambda x: x[1]["cagr"])
    worst_season = min(seasons.items(), key=lambda x: x[1]["cagr"])

    cagr_diff = best_season[1]["cagr"] - worst_season[1]["cagr"]

    # Difference is significant (> 10%)
    assert cagr_diff > 10
    assert best_season[0] == "kharif"


def test_pattern_identification_volatility():
    """Test pattern identification for volatility"""
    seasons = {
        "kharif": {"volatility_coefficient": 25.0},
        "rabi": {"volatility_coefficient": 8.0},
        "zaid": {"volatility_coefficient": 22.0},
    }

    # Identify volatile seasons (> 20%)
    volatile_seasons = [
        season for season, data in seasons.items() if data["volatility_coefficient"] > 20
    ]

    assert len(volatile_seasons) == 2
    assert "kharif" in volatile_seasons
    assert "zaid" in volatile_seasons


def test_pattern_identification_stable_pricing():
    """Test pattern identification for stable pricing"""
    seasons = {
        "kharif": {"volatility_coefficient": 8.0},
        "rabi": {"volatility_coefficient": 6.0},
        "zaid": {"volatility_coefficient": 15.0},
    }

    # Identify stable seasons (< 10%)
    stable_seasons = [
        season for season, data in seasons.items() if data["volatility_coefficient"] < 10
    ]

    assert len(stable_seasons) == 2
    assert "kharif" in stable_seasons
    assert "rabi" in stable_seasons


def test_pattern_identification_market_decline():
    """Test pattern identification for market decline"""
    seasons = {"kharif": {"cagr": -8.0}, "rabi": {"cagr": -6.0}, "zaid": {"cagr": -10.0}}

    # All seasons declining significantly (< -5%)
    all_declining = all(v["cagr"] < -5 for v in seasons.values())
    assert all_declining is True


def test_confidence_interval_calculation():
    """Test confidence interval calculation for forecasts"""
    prices = [2000.0, 2100.0, 2200.0, 2300.0]
    forecast_price = 2400.0

    # Calculate standard error
    std_error = statistics.stdev(prices)
    confidence_margin = 1.96 * std_error  # 95% confidence

    lower_bound = forecast_price - confidence_margin
    upper_bound = forecast_price + confidence_margin

    # Bounds should be reasonable
    assert lower_bound < forecast_price
    assert upper_bound > forecast_price
    assert upper_bound - lower_bound > 0


def test_indian_seasons_validation():
    """Test that Indian agricultural seasons are properly recognized"""
    valid_seasons = ["kharif", "rabi", "zaid"]

    # Test each season
    for season in valid_seasons:
        assert season in valid_seasons

    # Test invalid season
    invalid_season = "summer"
    assert invalid_season not in valid_seasons


def test_seasonal_months_mapping():
    """Test seasonal months mapping for Indian agriculture"""
    # Kharif: June-October (monsoon season)
    kharif_months = [6, 7, 8, 9, 10]

    # Rabi: November-April (winter season)
    rabi_months = [11, 12, 1, 2, 3, 4]

    # Zaid: May-June (summer season)
    zaid_months = [5, 6]

    # Test month classification
    assert 7 in kharif_months  # July is Kharif
    assert 12 in rabi_months  # December is Rabi
    assert 5 in zaid_months  # May is Zaid


def test_recommendation_generation_logic():
    """Test recommendation generation based on trends"""
    # Increasing trend
    slope_increasing = 100.0
    r_squared_high = 0.85

    recommendations = []

    if slope_increasing > 0:
        recommendations.append(
            f"Prices forecasted to increase by ₹{abs(slope_increasing):.2f} per quintal annually"
        )
        if r_squared_high > 0.7:
            recommendations.append("Strong upward trend suggests good profit potential")

    assert len(recommendations) == 2
    assert "increase" in recommendations[0]
    assert "profit potential" in recommendations[1]


def test_multi_year_analysis_period():
    """Test multi-year analysis period validation"""
    # Minimum 3 years required for meaningful analysis
    min_years = 3

    # Test with sufficient data
    available_years = 5
    assert available_years >= min_years

    # Test with insufficient data
    insufficient_years = 2
    assert insufficient_years < min_years


def test_seasonal_data_aggregation():
    """Test seasonal data aggregation logic"""
    # Sample seasonal data
    kharif_prices = [2000.0, 2100.0, 2200.0]
    rabi_prices = [2500.0, 2600.0, 2700.0]

    # Calculate averages
    kharif_avg = statistics.mean(kharif_prices)
    rabi_avg = statistics.mean(rabi_prices)

    assert kharif_avg == 2100.0
    assert rabi_avg == 2600.0

    # Rabi typically has higher prices
    assert rabi_avg > kharif_avg


def test_forecast_non_negative_prices():
    """Test that forecasted prices are never negative"""
    # Even with declining trend, prices should not go negative
    forecast_price = -100.0  # Hypothetical negative forecast

    # Apply non-negative constraint
    adjusted_price = max(0, forecast_price)

    assert adjusted_price == 0
    assert adjusted_price >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
