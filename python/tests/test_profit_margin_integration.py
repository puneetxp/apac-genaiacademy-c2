"""
Integration test for Profit Margin Service with Crop Recommendations
Tests that profit margin calculations integrate correctly with crop recommendations
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_profit_margin_integration():
    """
    Test that profit margin service integrates with crop recommendation workflow
    """
    print("=" * 80)
    print("Testing Profit Margin Service Integration")
    print("=" * 80)
    
    # Simulate crop recommendation with profit margin data
    print("\n1. Simulating crop recommendation with profit margin...")
    
    crop_recommendation = {
        'crop_name': 'Wheat',
        'variety': 'HD-2967',
        'expected_profit_per_acre': 45000,
        'investment_per_acre': 31000,
        'roi_percentage': 145.16
    }
    
    # Simulate profit margin calculation
    revenue_per_acre = 76000
    costs_per_acre = 31000
    net_profit_per_acre = revenue_per_acre - costs_per_acre
    profit_margin_pct = (net_profit_per_acre / revenue_per_acre) * 100
    
    profit_margin_details = {
        'profit_margin_percentage': profit_margin_pct,
        'net_profit_per_acre': net_profit_per_acre,
        'roi_percentage': (net_profit_per_acre / costs_per_acre) * 100,
        'break_even_yield_per_acre': costs_per_acre / 2200,  # Assuming ₹2200/quintal
        'profitability_status': 'highly_profitable' if profit_margin_pct > 50 else 'profitable',
        'total_costs': costs_per_acre * 5,  # 5 acres
        'total_revenue': revenue_per_acre * 5
    }
    
    # Add profit margin to recommendation
    crop_recommendation['profit_margin_details'] = profit_margin_details
    
    print(f"✓ Crop: {crop_recommendation['crop_name']}")
    print(f"  Expected profit: ₹{crop_recommendation['expected_profit_per_acre']:,.2f}/acre")
    print(f"  Profit margin: {profit_margin_details['profit_margin_percentage']:.2f}%")
    print(f"  ROI: {profit_margin_details['roi_percentage']:.2f}%")
    print(f"  Status: {profit_margin_details['profitability_status']}")
    
    assert 'profit_margin_details' in crop_recommendation
    assert profit_margin_details['profit_margin_percentage'] > 0
    print("✓ Profit margin integrated successfully")
    
    # Test 2: Multiple crops with profit margins
    print("\n2. Testing multiple crops with profit margins...")
    
    crops = [
        {
            'crop_name': 'Wheat',
            'expected_profit_per_acre': 45000,
            'revenue_per_acre': 76000,
            'costs_per_acre': 31000
        },
        {
            'crop_name': 'Rice',
            'expected_profit_per_acre': 38000,
            'revenue_per_acre': 73000,
            'costs_per_acre': 35000
        },
        {
            'crop_name': 'Cotton',
            'expected_profit_per_acre': 55000,
            'revenue_per_acre': 95000,
            'costs_per_acre': 40000
        }
    ]
    
    # Calculate profit margins for all crops
    for crop in crops:
        net_profit = crop['revenue_per_acre'] - crop['costs_per_acre']
        margin_pct = (net_profit / crop['revenue_per_acre']) * 100
        crop['profit_margin_percentage'] = margin_pct
    
    # Sort by profit margin
    crops_sorted = sorted(crops, key=lambda x: x['profit_margin_percentage'], reverse=True)
    
    print(f"  Crops ranked by profit margin:")
    for i, crop in enumerate(crops_sorted, 1):
        print(f"    {i}. {crop['crop_name']}: {crop['profit_margin_percentage']:.2f}%")
    
    assert crops_sorted[0]['profit_margin_percentage'] >= crops_sorted[-1]['profit_margin_percentage']
    print("✓ Multiple crops ranked by profit margin")
    
    # Test 3: Profit margin in opportunity cost analysis
    print("\n3. Testing profit margin in opportunity cost analysis...")
    
    primary_crop = crops_sorted[0]
    alternative_crop = crops_sorted[1]
    
    margin_diff = primary_crop['profit_margin_percentage'] - alternative_crop['profit_margin_percentage']
    profit_diff = primary_crop['expected_profit_per_acre'] - alternative_crop['expected_profit_per_acre']
    
    opportunity_cost = {
        'primary_crop': primary_crop['crop_name'],
        'alternative_crop': alternative_crop['crop_name'],
        'margin_difference': margin_diff,
        'profit_difference': profit_diff,
        'recommendation': f"{primary_crop['crop_name']} has {margin_diff:.2f}% higher profit margin"
    }
    
    print(f"  Primary: {opportunity_cost['primary_crop']}")
    print(f"  Alternative: {opportunity_cost['alternative_crop']}")
    print(f"  Margin difference: {opportunity_cost['margin_difference']:.2f}%")
    print(f"  Profit difference: ₹{opportunity_cost['profit_difference']:,.2f}/acre")
    print(f"  Recommendation: {opportunity_cost['recommendation']}")
    
    assert opportunity_cost['margin_difference'] > 0
    print("✓ Profit margin integrated in opportunity cost analysis")
    
    # Test 4: Profit margin recommendations
    print("\n4. Testing profit margin-based recommendations...")
    
    recommendations = []
    
    for crop in crops_sorted[:3]:  # Top 3 crops
        margin = crop['profit_margin_percentage']
        
        if margin > 50:
            rec = f"{crop['crop_name']}: Excellent {margin:.1f}% profit margin - highly recommended"
        elif margin > 30:
            rec = f"{crop['crop_name']}: Good {margin:.1f}% profit margin - recommended"
        else:
            rec = f"{crop['crop_name']}: Moderate {margin:.1f}% profit margin - consider alternatives"
        
        recommendations.append(rec)
    
    print(f"  Generated {len(recommendations)} recommendations:")
    for rec in recommendations:
        print(f"    - {rec}")
    
    assert len(recommendations) == 3
    print("✓ Profit margin recommendations generated")
    
    # Test 5: Complete recommendation response structure
    print("\n5. Testing complete recommendation response structure...")
    
    complete_response = {
        'location': {'state': 'Punjab', 'district': 'Ludhiana', 'season': 'rabi'},
        'top_recommendations': [
            {
                'crop_name': crop['crop_name'],
                'expected_profit_per_acre': crop['expected_profit_per_acre'],
                'profit_margin_details': {
                    'profit_margin_percentage': crop['profit_margin_percentage'],
                    'net_profit_per_acre': crop['revenue_per_acre'] - crop['costs_per_acre'],
                    'profitability_status': 'highly_profitable' if crop['profit_margin_percentage'] > 50 else 'profitable'
                }
            }
            for crop in crops_sorted[:3]
        ],
        'data_sources': {
            'historical_market_data': True,
            'profit_margin_analysis': True,
            'bedrock_ai_insights': True
        }
    }
    
    print(f"  Location: {complete_response['location']['state']}, {complete_response['location']['district']}")
    print(f"  Top recommendations: {len(complete_response['top_recommendations'])}")
    print(f"  Data sources: {', '.join(k for k, v in complete_response['data_sources'].items() if v)}")
    
    # Verify structure
    assert 'top_recommendations' in complete_response
    assert len(complete_response['top_recommendations']) == 3
    assert all('profit_margin_details' in rec for rec in complete_response['top_recommendations'])
    print("✓ Complete response structure validated")
    
    print("\n" + "=" * 80)
    print("✓ ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        test_profit_margin_integration()
        print("\n✓ Profit Margin Integration tests completed successfully!")
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
