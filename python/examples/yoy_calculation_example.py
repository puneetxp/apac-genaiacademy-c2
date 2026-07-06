"""
Example demonstrating YoY growth calculation algorithms
This script shows how the YoY calculations work without requiring database setup
"""

from decimal import Decimal
from typing import List, Dict, Any


class SimpleMarketData:
    """Simple market data structure for demonstration"""
    def __init__(self, year: int, price: Decimal):
        self.year = year
        self.avg_price_per_quintal = price


def calculate_yoy_growth_example(current_price: float, previous_price: float) -> Dict[str, Any]:
    """
    Example YoY growth calculation
    
    Args:
        current_price: Current year average price
        previous_price: Previous year average price
    
    Returns:
        Dictionary with YoY metrics
    """
    # Calculate YoY growth percentage
    yoy_growth_percentage = ((current_price - previous_price) / previous_price) * 100
    
    # Calculate absolute change
    absolute_change = current_price - previous_price
    
    # Determine trend
    if yoy_growth_percentage > 5:
        trend = 'increasing'
    elif yoy_growth_percentage < -5:
        trend = 'decreasing'
    else:
        trend = 'stable'
    
    return {
        'current_price': current_price,
        'previous_price': previous_price,
        'yoy_growth_percentage': round(yoy_growth_percentage, 2),
        'absolute_change': round(absolute_change, 2),
        'trend': trend
    }


def calculate_cagr_example(first_price: float, last_price: float, num_years: int) -> float:
    """
    Example CAGR calculation
    
    Args:
        first_price: Starting price
        last_price: Ending price
        num_years: Number of years
    
    Returns:
        CAGR percentage
    """
    cagr = (((last_price / first_price) ** (1 / num_years)) - 1) * 100
    return round(cagr, 2)


def calculate_multi_year_growth_example(year_prices: List[tuple]) -> Dict[str, Any]:
    """
    Example multi-year growth calculation
    
    Args:
        year_prices: List of (year, price) tuples
    
    Returns:
        Dictionary with multi-year growth metrics
    """
    if len(year_prices) < 2:
        return {'error': 'Insufficient data'}
    
    # Sort by year
    year_prices = sorted(year_prices, key=lambda x: x[0])
    
    # Calculate year-over-year changes
    yoy_changes = []
    for i in range(1, len(year_prices)):
        prev_year, prev_price = year_prices[i-1]
        curr_year, curr_price = year_prices[i]
        
        yoy_change = ((curr_price - prev_price) / prev_price) * 100
        
        yoy_changes.append({
            'from_year': prev_year,
            'to_year': curr_year,
            'previous_price': prev_price,
            'current_price': curr_price,
            'yoy_growth_percentage': round(yoy_change, 2),
            'absolute_change': round(curr_price - prev_price, 2)
        })
    
    # Calculate CAGR
    first_year, first_price = year_prices[0]
    last_year, last_price = year_prices[-1]
    num_years = len(year_prices) - 1
    
    cagr = calculate_cagr_example(first_price, last_price, num_years)
    
    # Calculate average YoY growth
    avg_yoy_growth = sum(change['yoy_growth_percentage'] for change in yoy_changes) / len(yoy_changes)
    
    # Determine overall trend
    if cagr > 5:
        overall_trend = 'strong_growth'
    elif cagr > 0:
        overall_trend = 'moderate_growth'
    elif cagr > -5:
        overall_trend = 'slight_decline'
    else:
        overall_trend = 'significant_decline'
    
    return {
        'analysis_period': {
            'start_year': first_year,
            'end_year': last_year,
            'years_analyzed': len(year_prices)
        },
        'price_summary': {
            'first_year_price': first_price,
            'last_year_price': last_price,
            'min_price': min(p for _, p in year_prices),
            'max_price': max(p for _, p in year_prices),
        },
        'growth_metrics': {
            'cagr': cagr,
            'avg_yoy_growth': round(avg_yoy_growth, 2),
            'overall_trend': overall_trend,
            'total_growth_percentage': round(((last_price - first_price) / first_price) * 100, 2)
        },
        'yearly_breakdown': yoy_changes
    }


def main():
    """Run example calculations"""
    print("=" * 80)
    print("YoY Growth Calculation Examples")
    print("=" * 80)
    
    # Example 1: Basic YoY Growth
    print("\n1. Basic YoY Growth Calculation")
    print("-" * 80)
    print("Scenario: Wheat prices in Punjab")
    print("  2023: ₹2000/quintal")
    print("  2024: ₹2200/quintal")
    
    result = calculate_yoy_growth_example(2200.00, 2000.00)
    print(f"\nResults:")
    print(f"  YoY Growth: {result['yoy_growth_percentage']}%")
    print(f"  Absolute Change: ₹{result['absolute_change']}/quintal")
    print(f"  Trend: {result['trend']}")
    
    # Example 2: Decreasing Prices
    print("\n2. Decreasing Price Trend")
    print("-" * 80)
    print("Scenario: Rice prices in Bihar")
    print("  2023: ₹2000/quintal")
    print("  2024: ₹1800/quintal")
    
    result = calculate_yoy_growth_example(1800.00, 2000.00)
    print(f"\nResults:")
    print(f"  YoY Growth: {result['yoy_growth_percentage']}%")
    print(f"  Absolute Change: ₹{result['absolute_change']}/quintal")
    print(f"  Trend: {result['trend']}")
    
    # Example 3: Stable Prices
    print("\n3. Stable Price Trend")
    print("-" * 80)
    print("Scenario: Cotton prices in Gujarat")
    print("  2023: ₹5000/quintal")
    print("  2024: ₹5100/quintal")
    
    result = calculate_yoy_growth_example(5100.00, 5000.00)
    print(f"\nResults:")
    print(f"  YoY Growth: {result['yoy_growth_percentage']}%")
    print(f"  Absolute Change: ₹{result['absolute_change']}/quintal")
    print(f"  Trend: {result['trend']}")
    
    # Example 4: Multi-Year Growth with CAGR
    print("\n4. Multi-Year Growth Analysis (5 years)")
    print("-" * 80)
    print("Scenario: Wheat prices in Punjab (2020-2024)")
    
    year_prices = [
        (2020, 1800.00),
        (2021, 1900.00),
        (2022, 2000.00),
        (2023, 2100.00),
        (2024, 2200.00)
    ]
    
    for year, price in year_prices:
        print(f"  {year}: ₹{price}/quintal")
    
    result = calculate_multi_year_growth_example(year_prices)
    print(f"\nResults:")
    print(f"  CAGR: {result['growth_metrics']['cagr']}%")
    print(f"  Average YoY Growth: {result['growth_metrics']['avg_yoy_growth']}%")
    print(f"  Total Growth: {result['growth_metrics']['total_growth_percentage']}%")
    print(f"  Overall Trend: {result['growth_metrics']['overall_trend']}")
    print(f"  Price Range: ₹{result['price_summary']['min_price']} - ₹{result['price_summary']['max_price']}")
    
    print("\n  Year-by-Year Breakdown:")
    for change in result['yearly_breakdown']:
        print(f"    {change['from_year']} → {change['to_year']}: "
              f"{change['yoy_growth_percentage']:+.2f}% "
              f"(₹{change['previous_price']} → ₹{change['current_price']})")
    
    # Example 5: Strong Growth Scenario
    print("\n5. Strong Growth Scenario")
    print("-" * 80)
    print("Scenario: Organic produce prices (2020-2024)")
    
    year_prices = [
        (2020, 3000.00),
        (2021, 3300.00),
        (2022, 3700.00),
        (2023, 4200.00),
        (2024, 4800.00)
    ]
    
    for year, price in year_prices:
        print(f"  {year}: ₹{price}/quintal")
    
    result = calculate_multi_year_growth_example(year_prices)
    print(f"\nResults:")
    print(f"  CAGR: {result['growth_metrics']['cagr']}%")
    print(f"  Average YoY Growth: {result['growth_metrics']['avg_yoy_growth']}%")
    print(f"  Total Growth: {result['growth_metrics']['total_growth_percentage']}%")
    print(f"  Overall Trend: {result['growth_metrics']['overall_trend']}")
    
    # Example 6: Declining Market
    print("\n6. Declining Market Scenario")
    print("-" * 80)
    print("Scenario: Oversupplied crop (2020-2024)")
    
    year_prices = [
        (2020, 2500.00),
        (2021, 2400.00),
        (2022, 2250.00),
        (2023, 2100.00),
        (2024, 1950.00)
    ]
    
    for year, price in year_prices:
        print(f"  {year}: ₹{price}/quintal")
    
    result = calculate_multi_year_growth_example(year_prices)
    print(f"\nResults:")
    print(f"  CAGR: {result['growth_metrics']['cagr']}%")
    print(f"  Average YoY Growth: {result['growth_metrics']['avg_yoy_growth']}%")
    print(f"  Total Growth: {result['growth_metrics']['total_growth_percentage']}%")
    print(f"  Overall Trend: {result['growth_metrics']['overall_trend']}")
    
    print("\n" + "=" * 80)
    print("Examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
