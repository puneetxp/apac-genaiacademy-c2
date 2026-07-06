"""
Example usage of Seasonal Trend Analysis Service

This script demonstrates how to use the seasonal trend analysis service
to analyze crop trends across Indian agricultural seasons.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.seasonal_trend_service import SeasonalTrendService
from app.services.market_data_service import MarketDataService
from app.core.database import SessionLocal
import json


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_json(data, indent=2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent, default=str))


def example_1_analyze_all_seasons():
    """Example 1: Analyze all seasons for a crop"""
    print_section("Example 1: Analyze All Seasons for Wheat in Punjab")
    
    db = SessionLocal()
    try:
        service = SeasonalTrendService(db)
        
        # Analyze all seasons for Wheat in Punjab
        result = service.analyze_seasonal_trends(
            crop_type="Wheat",
            state="Punjab",
            years=5
        )
        
        print("Analysis Results:")
        print_json(result)
        
        # Extract key insights
        if result.get('comparison'):
            print("\n📊 Key Insights:")
            best_season = result['comparison'].get('best_price_growth', {})
            if best_season:
                print(f"  • Best Season: {best_season['season'].capitalize()}")
                print(f"  • CAGR: {best_season['cagr']:.2f}%")
            
            stable_season = result['comparison'].get('most_stable', {})
            if stable_season:
                print(f"  • Most Stable: {stable_season['season'].capitalize()}")
                print(f"  • Volatility: {stable_season['volatility']:.2f}%")
        
        if result.get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
    
    finally:
        db.close()


def example_2_analyze_specific_season():
    """Example 2: Analyze a specific season"""
    print_section("Example 2: Analyze Rabi Season for Wheat in Punjab")
    
    db = SessionLocal()
    try:
        service = SeasonalTrendService(db)
        
        # Analyze Rabi season specifically
        result = service.analyze_season_trend(
            crop_type="Wheat",
            state="Punjab",
            season="rabi",
            years=5
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print("Season Analysis:")
        print_json(result)
        
        # Extract season info
        if result.get('season_info'):
            info = result['season_info']
            print("\n🌾 Season Information:")
            print(f"  • Name: {info.get('name')}")
            print(f"  • Planting: {info.get('planting_months')}")
            print(f"  • Harvest: {info.get('harvest_months')}")
            print(f"  • Key Factor: {info.get('key_factor')}")
        
        # Extract price metrics
        if result.get('price_metrics'):
            metrics = result['price_metrics']
            print("\n💰 Price Metrics:")
            print(f"  • Average Price: ₹{metrics.get('avg_price', 0):.2f}/quintal")
            print(f"  • CAGR: {metrics.get('cagr', 0):.2f}%")
            print(f"  • Volatility: {metrics.get('volatility_coefficient', 0):.2f}%")
        
        # Extract recommendations
        if result.get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
    
    finally:
        db.close()


def example_3_forecast_prices():
    """Example 3: Forecast seasonal prices"""
    print_section("Example 3: Forecast Rabi Season Prices for Wheat")
    
    db = SessionLocal()
    try:
        service = SeasonalTrendService(db)
        
        # Forecast prices for next 2 years
        result = service.forecast_seasonal_prices(
            crop_type="Wheat",
            state="Punjab",
            season="rabi",
            forecast_years=2
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print("Price Forecast:")
        print_json(result)
        
        # Extract forecast summary
        if result.get('historical_summary'):
            summary = result['historical_summary']
            print("\n📈 Historical Summary:")
            print(f"  • Years Analyzed: {summary.get('years_analyzed')}")
            print(f"  • Avg Historical Price: ₹{summary.get('avg_historical_price', 0):.2f}")
            print(f"  • Price Trend: {summary.get('price_trend')}")
            print(f"  • Annual Change: ₹{summary.get('annual_change_rate', 0):.2f}")
        
        # Extract forecasts
        if result.get('forecast', {}).get('predictions'):
            predictions = result['forecast']['predictions']
            reliability = result['forecast'].get('reliability', 'unknown')
            
            print(f"\n🔮 Forecasts (Reliability: {reliability.upper()}):")
            for pred in predictions:
                print(f"\n  Year {pred['year']}:")
                print(f"    • Forecast Price: ₹{pred['forecast_price']:.2f}/quintal")
                print(f"    • Range: ₹{pred['lower_bound']:.2f} - ₹{pred['upper_bound']:.2f}")
                print(f"    • Confidence: {pred['confidence_score']:.2%}")
        
        # Extract recommendations
        if result.get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
    
    finally:
        db.close()


def example_4_identify_patterns():
    """Example 4: Identify seasonal patterns"""
    print_section("Example 4: Identify Seasonal Patterns for Cotton in Gujarat")
    
    db = SessionLocal()
    try:
        service = SeasonalTrendService(db)
        
        # Identify patterns across seasons
        result = service.identify_seasonal_patterns(
            crop_type="Cotton",
            state="Gujarat"
        )
        
        print("Pattern Analysis:")
        print_json(result)
        
        # Extract identified patterns
        if result.get('identified_patterns'):
            patterns = result['identified_patterns']
            print(f"\n🔍 Identified {len(patterns)} Pattern(s):")
            
            for i, pattern in enumerate(patterns, 1):
                print(f"\n  Pattern {i}: {pattern.get('pattern', 'unknown').upper()}")
                print(f"    • Description: {pattern.get('description')}")
                print(f"    • Recommendation: {pattern.get('recommendation')}")
                print(f"    • Confidence: {pattern.get('confidence', 'unknown').upper()}")
                
                if pattern.get('best_season'):
                    print(f"    • Best Season: {pattern['best_season'].capitalize()}")
                if pattern.get('affected_seasons'):
                    seasons = ', '.join(s.capitalize() for s in pattern['affected_seasons'])
                    print(f"    • Affected Seasons: {seasons}")
    
    finally:
        db.close()


def example_5_yoy_growth():
    """Example 5: Calculate Year-over-Year growth"""
    print_section("Example 5: Calculate YoY Growth for Wheat in Punjab")
    
    db = SessionLocal()
    try:
        service = MarketDataService(db)
        
        # Calculate YoY growth
        result = service.calculate_yoy_growth(
            crop_type="Wheat",
            state="Punjab",
            season="rabi"
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print("YoY Growth Analysis:")
        print_json(result)
        
        # Extract key metrics
        print("\n📊 Key Metrics:")
        print(f"  • Current Year: {result.get('current_year')}")
        print(f"  • Previous Year: {result.get('previous_year')}")
        print(f"  • Current Avg Price: ₹{result.get('current_avg_price', 0):.2f}")
        print(f"  • Previous Avg Price: ₹{result.get('previous_avg_price', 0):.2f}")
        print(f"  • YoY Growth: {result.get('yoy_growth_percentage', 0):.2f}%")
        print(f"  • Absolute Change: ₹{result.get('absolute_change', 0):.2f}")
        print(f"  • Trend: {result.get('trend', 'unknown').upper()}")
    
    finally:
        db.close()


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("  SEASONAL TREND ANALYSIS SERVICE - EXAMPLES")
    print("=" * 80)
    
    examples = [
        ("Analyze All Seasons", example_1_analyze_all_seasons),
        ("Analyze Specific Season", example_2_analyze_specific_season),
        ("Forecast Prices", example_3_forecast_prices),
        ("Identify Patterns", example_4_identify_patterns),
        ("YoY Growth", example_5_yoy_growth)
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print("  0. Run All Examples")
    
    try:
        choice = input("\nSelect example (0-5): ").strip()
        
        if choice == '0':
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n❌ Error in {name}: {e}")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            name, func = examples[int(choice) - 1]
            func()
        else:
            print("Invalid choice!")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("  Examples Complete")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
