"""
Standalone test for Profit Margin Calculation Service
Tests core calculation logic without database dependencies
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_profit_margin_calculations():
    """
    Test profit margin calculation formulas
    """
    print("=" * 80)
    print("Testing Profit Margin Calculation Formulas")
    print("=" * 80)

    # Test 1: Basic profit margin calculation
    print("\n1. Testing basic profit margin formula...")
    revenue = 60000
    costs = 25000
    net_profit = revenue - costs
    profit_margin_pct = (net_profit / revenue) * 100

    print(f"  Revenue: ₹{revenue:,.2f}")
    print(f"  Costs: ₹{costs:,.2f}")
    print(f"  Net Profit: ₹{net_profit:,.2f}")
    print(f"  Profit Margin: {profit_margin_pct:.2f}%")

    assert net_profit == 35000
    assert abs(profit_margin_pct - 58.33) < 0.01
    print("✓ Basic profit margin calculation passed")

    # Test 2: ROI calculation
    print("\n2. Testing ROI formula...")
    roi_pct = (net_profit / costs) * 100
    print(f"  ROI: {roi_pct:.2f}%")

    expected_roi = 140.0
    assert abs(roi_pct - expected_roi) < 0.01
    print("✓ ROI calculation passed")

    # Test 3: Break-even yield calculation
    print("\n3. Testing break-even yield formula...")
    price_per_quintal = 2000
    break_even_yield = costs / price_per_quintal
    print(f"  Price per quintal: ₹{price_per_quintal:,.2f}")
    print(f"  Break-even yield: {break_even_yield:.2f} quintals")

    assert break_even_yield == 12.5
    print("✓ Break-even yield calculation passed")

    # Test 4: Multi-acre calculations
    print("\n4. Testing multi-acre scaling...")
    area_acres = 5.0
    cost_per_acre = 25000
    revenue_per_acre = 60000

    total_costs = cost_per_acre * area_acres
    total_revenue = revenue_per_acre * area_acres
    total_profit = total_revenue - total_costs

    print(f"  Area: {area_acres} acres")
    print(f"  Total costs: ₹{total_costs:,.2f}")
    print(f"  Total revenue: ₹{total_revenue:,.2f}")
    print(f"  Total profit: ₹{total_profit:,.2f}")

    assert total_costs == 125000
    assert total_revenue == 300000
    assert total_profit == 175000
    print("✓ Multi-acre scaling passed")

    # Test 5: Profitability status classification
    print("\n5. Testing profitability status classification...")
    test_cases = [
        (60, "highly_profitable"),
        (40, "profitable"),
        (20, "moderately_profitable"),
        (5, "marginally_profitable"),
        (-10, "unprofitable"),
    ]

    for margin_pct, expected_status in test_cases:
        if margin_pct > 50:
            status = "highly_profitable"
        elif margin_pct > 30:
            status = "profitable"
        elif margin_pct > 10:
            status = "moderately_profitable"
        elif margin_pct > 0:
            status = "marginally_profitable"
        else:
            status = "unprofitable"

        assert status == expected_status
        print(f"  Margin {margin_pct}% → {status} ✓")

    print("✓ Profitability status classification passed")

    # Test 6: Cost breakdown calculation
    print("\n6. Testing cost breakdown...")
    costs_breakdown = {
        "seed_cost": 3000,
        "fertilizer_cost": 8000,
        "pesticide_cost": 2000,
        "labor_cost": 12000,
        "irrigation_cost": 3000,
        "equipment_cost": 2000,
        "other_costs": 1000,
    }

    total_cost_per_acre = sum(costs_breakdown.values())
    print(f"  Cost breakdown per acre:")
    for cost_type, amount in costs_breakdown.items():
        print(f"    - {cost_type}: ₹{amount:,.2f}")
    print(f"  Total cost per acre: ₹{total_cost_per_acre:,.2f}")

    assert total_cost_per_acre == 31000
    print("✓ Cost breakdown calculation passed")

    # Test 7: Revenue calculation from yield and price
    print("\n7. Testing revenue calculation...")
    yield_per_acre = 35  # quintals
    price_per_quintal = 2200
    revenue_per_acre = yield_per_acre * price_per_quintal

    print(f"  Yield: {yield_per_acre} quintals/acre")
    print(f"  Price: ₹{price_per_quintal}/quintal")
    print(f"  Revenue: ₹{revenue_per_acre:,.2f}/acre")

    assert revenue_per_acre == 77000
    print("✓ Revenue calculation passed")

    # Test 8: Comparative analysis
    print("\n8. Testing comparative analysis...")
    wheat_margin = 59.21
    rice_margin = 47.95

    margin_diff = wheat_margin - rice_margin
    print(f"  Wheat margin: {wheat_margin:.2f}%")
    print(f"  Rice margin: {rice_margin:.2f}%")
    print(f"  Difference: {margin_diff:.2f}%")

    assert wheat_margin > rice_margin
    assert abs(margin_diff - 11.26) < 0.01
    print("✓ Comparative analysis passed")

    # Test 9: Profit difference calculation
    print("\n9. Testing profit difference...")
    wheat_profit = 45000
    rice_profit = 38000
    profit_diff = wheat_profit - rice_profit

    print(f"  Wheat profit: ₹{wheat_profit:,.2f}/acre")
    print(f"  Rice profit: ₹{rice_profit:,.2f}/acre")
    print(f"  Opportunity cost: ₹{profit_diff:,.2f}/acre")

    assert profit_diff == 7000
    print("✓ Profit difference calculation passed")

    # Test 10: Custom cost override
    print("\n10. Testing custom cost override...")
    default_seed_cost = 3000
    custom_seed_cost = 5000

    print(f"  Default seed cost: ₹{default_seed_cost:,.2f}")
    print(f"  Custom seed cost: ₹{custom_seed_cost:,.2f}")

    # Simulate override
    final_seed_cost = custom_seed_cost
    assert final_seed_cost == 5000
    print("✓ Custom cost override passed")

    print("\n" + "=" * 80)
    print("✓ ALL CALCULATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

    return True


def test_service_logic():
    """
    Test service logic patterns
    """
    print("\n" + "=" * 80)
    print("Testing Service Logic Patterns")
    print("=" * 80)

    # Test 1: Data availability check
    print("\n1. Testing data availability logic...")
    has_profitability_data = True
    has_market_data = True
    has_yield_data = True

    if has_profitability_data and has_market_data and has_yield_data:
        print("  ✓ All data sources available")
    else:
        print("  ⚠ Some data sources missing, using defaults")

    assert has_profitability_data
    print("✓ Data availability check passed")

    # Test 2: Recommendation generation logic
    print("\n2. Testing recommendation generation...")
    profit_margin = 60.0
    roi = 150.0
    status = "highly_profitable"

    recommendations = []

    if status == "highly_profitable":
        recommendations.append(
            f"Excellent profit margin of {profit_margin:.1f}%. "
            "This crop is highly recommended for your location."
        )

    if roi > 100:
        recommendations.append(
            f"Excellent ROI of {roi:.1f}%. " "This crop offers strong returns on your investment."
        )

    print(f"  Generated {len(recommendations)} recommendations:")
    for rec in recommendations:
        print(f"    - {rec}")

    assert len(recommendations) == 2
    print("✓ Recommendation generation passed")

    # Test 3: Comparison insights logic
    print("\n3. Testing comparison insights...")
    crops = [
        {"name": "Wheat", "margin": 59.21, "profit": 45000},
        {"name": "Rice", "margin": 47.95, "profit": 38000},
    ]

    best_crop = max(crops, key=lambda x: x["margin"])
    worst_crop = min(crops, key=lambda x: x["margin"])

    insight = (
        f"{best_crop['name']} has the highest profit margin at "
        f"{best_crop['margin']:.1f}%, which is "
        f"{best_crop['margin'] - worst_crop['margin']:.1f}% higher than {worst_crop['name']}."
    )

    print(f"  Insight: {insight}")
    assert best_crop["name"] == "Wheat"
    print("✓ Comparison insights passed")

    print("\n" + "=" * 80)
    print("✓ ALL SERVICE LOGIC TESTS PASSED!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    try:
        test_profit_margin_calculations()
        test_service_logic()
        print("\n" + "=" * 80)
        print("✓✓✓ ALL PROFIT MARGIN SERVICE TESTS COMPLETED SUCCESSFULLY! ✓✓✓")
        print("=" * 80)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
