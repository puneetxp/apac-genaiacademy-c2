"""
Sample script to ingest market data
Demonstrates how to use the market data ingestion service
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.market_data_service import MarketDataService


def ingest_sample_crop_market_data(db: Session):
    """Ingest sample crop market data"""
    
    service = MarketDataService(db)
    
    # Sample market data for different crops and states
    sample_data = [
        # Wheat data - Punjab
        {
            "crop_type": "Wheat",
            "variety": "HD-2967",
            "state": "Punjab",
            "district": "Ludhiana",
            "market_name": "Ludhiana Mandi",
            "year": 2023,
            "month": 4,
            "season": "rabi",
            "avg_price_per_quintal": 2150.50,
            "min_price": 2000.00,
            "max_price": 2300.00,
            "modal_price": 2150.00,
            "market_demand_score": 0.85,
            "supply_volume": 50000.00,
            "price_volatility": 5.2,
            "price_trend": "increasing",
            "yoy_price_change": 8.5,
            "mom_price_change": 2.3,
            "data_source": "AGMARKNET",
            "data_quality_score": 0.95
        },
        {
            "crop_type": "Wheat",
            "variety": "HD-2967",
            "state": "Punjab",
            "district": "Ludhiana",
            "year": 2022,
            "month": 4,
            "season": "rabi",
            "avg_price_per_quintal": 1980.00,
            "min_price": 1850.00,
            "max_price": 2100.00,
            "modal_price": 1980.00,
            "market_demand_score": 0.80,
            "price_trend": "stable",
            "yoy_price_change": 5.2,
            "data_source": "AGMARKNET",
            "data_quality_score": 0.90
        },
        # Rice data - Punjab
        {
            "crop_type": "Rice",
            "variety": "Basmati",
            "state": "Punjab",
            "district": "Amritsar",
            "market_name": "Amritsar Mandi",
            "year": 2023,
            "month": 10,
            "season": "kharif",
            "avg_price_per_quintal": 3500.00,
            "min_price": 3200.00,
            "max_price": 3800.00,
            "modal_price": 3500.00,
            "market_demand_score": 0.90,
            "supply_volume": 40000.00,
            "price_volatility": 7.5,
            "price_trend": "increasing",
            "yoy_price_change": 12.5,
            "mom_price_change": 3.8,
            "data_source": "AGMARKNET",
            "data_quality_score": 0.95
        },
        # Cotton data - Gujarat
        {
            "crop_type": "Cotton",
            "variety": "BT Cotton",
            "state": "Gujarat",
            "district": "Ahmedabad",
            "market_name": "Ahmedabad Cotton Market",
            "year": 2023,
            "month": 11,
            "season": "kharif",
            "avg_price_per_quintal": 6500.00,
            "min_price": 6000.00,
            "max_price": 7000.00,
            "modal_price": 6500.00,
            "market_demand_score": 0.75,
            "supply_volume": 30000.00,
            "price_volatility": 10.2,
            "price_trend": "stable",
            "yoy_price_change": 3.5,
            "data_source": "manual",
            "data_quality_score": 0.85
        },
        # Sugarcane data - Maharashtra
        {
            "crop_type": "Sugarcane",
            "state": "Maharashtra",
            "district": "Pune",
            "year": 2023,
            "month": 12,
            "season": "kharif",
            "avg_price_per_quintal": 350.00,
            "min_price": 320.00,
            "max_price": 380.00,
            "modal_price": 350.00,
            "market_demand_score": 0.88,
            "price_trend": "increasing",
            "yoy_price_change": 6.0,
            "data_source": "manual",
            "data_quality_score": 0.80
        },
        # Soybean data - Madhya Pradesh
        {
            "crop_type": "Soybean",
            "state": "Madhya Pradesh",
            "district": "Indore",
            "market_name": "Indore Mandi",
            "year": 2023,
            "month": 10,
            "season": "kharif",
            "avg_price_per_quintal": 4200.00,
            "min_price": 3900.00,
            "max_price": 4500.00,
            "modal_price": 4200.00,
            "market_demand_score": 0.82,
            "supply_volume": 25000.00,
            "price_volatility": 8.5,
            "price_trend": "increasing",
            "yoy_price_change": 10.2,
            "data_source": "AGMARKNET",
            "data_quality_score": 0.92
        }
    ]
    
    print("Ingesting sample crop market data...")
    result = service.bulk_ingest_crop_market_data(
        sample_data,
        validate=True,
        skip_errors=False
    )
    
    print(f"\nBulk ingestion completed:")
    print(f"  Success: {result['success_count']}")
    print(f"  Errors: {result['error_count']}")
    print(f"  Total: {result['total_records']}")
    
    if result['errors']:
        print("\nErrors encountered:")
        for error in result['errors']:
            print(f"  Record {error['index']}: {error['error']}")
    
    return result


def ingest_sample_yield_data(db: Session):
    """Ingest sample historical yield data"""
    
    service = MarketDataService(db)
    
    sample_yield_data = [
        {
            "crop_type": "Wheat",
            "variety": "HD-2967",
            "state": "Punjab",
            "district": "Ludhiana",
            "year": 2023,
            "season": "rabi",
            "avg_yield_per_acre": 22.5,
            "min_yield": 18.0,
            "max_yield": 26.0,
            "success_rate": 92.5,
            "farmer_count": 1500,
            "total_area_cultivated": 50000.0,
            "soil_types": ["loamy", "clay"],
            "irrigation_methods": ["canal", "tubewell"],
            "avg_rainfall": 650.0,
            "avg_temperature": 18.5,
            "quality_distribution": {"A": 0.65, "B": 0.30, "C": 0.05},
            "avg_quality_grade": "A",
            "data_source": "agricultural_survey",
            "data_quality_score": 0.90
        },
        {
            "crop_type": "Rice",
            "variety": "Basmati",
            "state": "Punjab",
            "district": "Amritsar",
            "year": 2023,
            "season": "kharif",
            "avg_yield_per_acre": 28.0,
            "min_yield": 22.0,
            "max_yield": 32.0,
            "success_rate": 88.0,
            "farmer_count": 2000,
            "total_area_cultivated": 60000.0,
            "soil_types": ["clay", "loamy"],
            "irrigation_methods": ["canal", "tubewell"],
            "avg_rainfall": 850.0,
            "avg_temperature": 28.0,
            "quality_distribution": {"A": 0.70, "B": 0.25, "C": 0.05},
            "avg_quality_grade": "A",
            "data_source": "agricultural_survey",
            "data_quality_score": 0.92
        }
    ]
    
    print("\nIngesting sample historical yield data...")
    for data in sample_yield_data:
        try:
            yield_record = service.ingest_historical_yield(data, validate=True)
            print(f"  ✓ Ingested: {data['crop_type']} - {data['state']} - {data['year']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")


def ingest_sample_profitability_data(db: Session):
    """Ingest sample crop profitability data"""
    
    service = MarketDataService(db)
    
    sample_profitability_data = [
        {
            "crop_type": "Wheat",
            "variety": "HD-2967",
            "state": "Punjab",
            "district": "Ludhiana",
            "year": 2023,
            "season": "rabi",
            "avg_profit_per_acre": 45000.0,
            "min_profit_per_acre": 35000.0,
            "max_profit_per_acre": 55000.0,
            "seed_cost": 3000.0,
            "fertilizer_cost": 8000.0,
            "pesticide_cost": 2500.0,
            "labor_cost": 12000.0,
            "irrigation_cost": 4000.0,
            "equipment_cost": 3500.0,
            "other_costs": 2000.0,
            "total_investment_cost": 35000.0,
            "avg_revenue_per_acre": 80000.0,
            "roi_percentage": 128.6,
            "break_even_yield": 16.3,
            "profit_margin": 56.3,
            "risk_level": "low",
            "price_risk_score": 0.25,
            "yield_risk_score": 0.20,
            "market_demand": "high",
            "competition_level": "medium",
            "data_source": "farm_survey",
            "sample_size": 500
        },
        {
            "crop_type": "Rice",
            "variety": "Basmati",
            "state": "Punjab",
            "district": "Amritsar",
            "year": 2023,
            "season": "kharif",
            "avg_profit_per_acre": 65000.0,
            "min_profit_per_acre": 50000.0,
            "max_profit_per_acre": 80000.0,
            "seed_cost": 4000.0,
            "fertilizer_cost": 10000.0,
            "pesticide_cost": 3500.0,
            "labor_cost": 15000.0,
            "irrigation_cost": 6000.0,
            "equipment_cost": 4000.0,
            "other_costs": 2500.0,
            "total_investment_cost": 45000.0,
            "avg_revenue_per_acre": 110000.0,
            "roi_percentage": 144.4,
            "break_even_yield": 12.9,
            "profit_margin": 59.1,
            "risk_level": "medium",
            "price_risk_score": 0.35,
            "yield_risk_score": 0.30,
            "market_demand": "high",
            "competition_level": "high",
            "data_source": "farm_survey",
            "sample_size": 600
        }
    ]
    
    print("\nIngesting sample crop profitability data...")
    for data in sample_profitability_data:
        try:
            profitability_record = service.ingest_crop_profitability(data, validate=True)
            print(f"  ✓ Ingested: {data['crop_type']} - {data['state']} - {data['year']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")


def main():
    """Main function to run sample data ingestion"""
    
    print("=" * 60)
    print("Market Data Ingestion - Sample Data")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Ingest crop market data
        ingest_sample_crop_market_data(db)
        
        # Ingest historical yield data
        ingest_sample_yield_data(db)
        
        # Ingest profitability data
        ingest_sample_profitability_data(db)
        
        # Get summary
        service = MarketDataService(db)
        summary = service.get_market_data_summary()
        
        print("\n" + "=" * 60)
        print("Market Data Summary")
        print("=" * 60)
        print(f"Total Records: {summary['total_records']}")
        print(f"Unique Crops: {summary['unique_crops']}")
        print(f"Unique States: {summary['unique_states']}")
        if summary['year_range']:
            print(f"Year Range: {summary['year_range']['min']} - {summary['year_range']['max']}")
        
        print("\n✓ Sample data ingestion completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
