"""
Unit tests for Profit Margin Calculation Service
"""

import sys
import os
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.types import Numeric as SQLDecimal
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

# Create a minimal Base for testing
Base = declarative_base()

# Minimal models for testing
class CropProfitability(Base):
    __tablename__ = "crop_profitability"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    crop_type = Column(String(100), nullable=False)
    variety = Column(String(200))
    state = Column(String(100), nullable=False)
    district = Column(String(100))
    year = Column(Integer, nullable=False)
    season = Column(String(50))
    avg_profit_per_acre = Column(SQLDecimal(10, 2), nullable=False)
    seed_cost = Column(SQLDecimal(10, 2))
    fertilizer_cost = Column(SQLDecimal(10, 2))
    pesticide_cost = Column(SQLDecimal(10, 2))
    labor_cost = Column(SQLDecimal(10, 2))
    irrigation_cost = Column(SQLDecimal(10, 2))
    equipment_cost = Column(SQLDecimal(10, 2))
    other_costs = Column(SQLDecimal(10, 2))
    total_investment_cost = Column(SQLDecimal(10, 2))
    avg_revenue_per_acre = Column(SQLDecimal(10, 2))
    roi_percentage = Column(SQLDecimal(5, 2))
    profit_margin = Column(SQLDecimal(5, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CropMarketData(Base):
    __tablename__ = "crop_market_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    crop_type = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    district = Column(String(100))
    year = Column(Integer, nullable=False)
    month = Column(Integer)
    season = Column(String(50))
    avg_price_per_quintal = Column(SQLDecimal(10, 2), nullable=False)
    min_price = Column(SQLDecimal(10, 2))
    max_price = Column(SQLDecimal(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HistoricalYield(Base):
    __tablename__ = "historical_yields"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    crop_type = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    district = Column(String(100))
    year = Column(Integer, nullable=False)
    season = Column(String(50))
    avg_yield_per_acre = Column(SQLDecimal(10, 2), nullable=False)
    success_rate = Column(SQLDecimal(5, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Import service after models
from app.services.profit_margin_service import ProfitMarginService


def test_profit_margin_calculation():
    """
    Test profit margin calculation with sample data
    """
    print("=" * 80)
    print("Testing Profit Margin Calculation Service")
    print("=" * 80)
    
    # Create in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create profit margin service
        profit_service = ProfitMarginService(session)
        
        # Test 1: Add sample profitability data
        print("\n1. Adding sample profitability data...")
        wheat_profitability = CropProfitability(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            year=2023,
            season="rabi",
            avg_profit_per_acre=Decimal("45000.00"),
            seed_cost=Decimal("3000.00"),
            fertilizer_cost=Decimal("8000.00"),
            pesticide_cost=Decimal("2000.00"),
            labor_cost=Decimal("12000.00"),
            irrigation_cost=Decimal("3000.00"),
            equipment_cost=Decimal("2000.00"),
            other_costs=Decimal("1000.00"),
            total_investment_cost=Decimal("31000.00"),
            avg_revenue_per_acre=Decimal("76000.00"),
            roi_percentage=Decimal("145.16"),
            profit_margin=Decimal("59.21")
        )
        session.add(wheat_profitability)
        
        # Add market data
        wheat_market = CropMarketData(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            year=2023,
            month=4,
            season="rabi",
            avg_price_per_quintal=Decimal("2200.00"),
            min_price=Decimal("2000.00"),
            max_price=Decimal("2400.00")
        )
        session.add(wheat_market)
        
        # Add yield data
        wheat_yield = HistoricalYield(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            year=2023,
            season="rabi",
            avg_yield_per_acre=Decimal("35.00"),
            success_rate=Decimal("85.00")
        )
        session.add(wheat_yield)
        session.commit()
        print("✓ Sample data added successfully")
        
        # Test 2: Calculate profit margin for wheat
        print("\n2. Calculating profit margin for Wheat in Punjab...")
        result = profit_service.calculate_profit_margin(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            season="rabi",
            area_acres=5.0
        )
        
        print(f"✓ Profit margin calculated successfully")
        print(f"  Crop: {result['crop_type']}")
        print(f"  Location: {result['location']['state']}, {result['location']['district']}")
        print(f"  Area: {result['area_acres']} acres")
        print(f"\n  Costs (per acre):")
        print(f"    - Seed: ₹{result['costs']['per_acre']['seed_cost']:,.2f}")
        print(f"    - Fertilizer: ₹{result['costs']['per_acre']['fertilizer_cost']:,.2f}")
        print(f"    - Labor: ₹{result['costs']['per_acre']['labor_cost']:,.2f}")
        print(f"    - Total: ₹{result['costs']['per_acre']['total_cost_per_acre']:,.2f}")
        print(f"\n  Revenue (per acre): ₹{result['revenue']['per_acre']['revenue_per_acre']:,.2f}")
        print(f"\n  Profit Margin:")
        print(f"    - Net Profit: ₹{result['profit_margin']['net_profit']:,.2f}")
        print(f"    - Profit Margin %: {result['profit_margin']['profit_margin_percentage']:.2f}%")
        print(f"    - ROI %: {result['profit_margin']['roi_percentage']:.2f}%")
        print(f"    - Status: {result['profit_margin']['profitability_status']}")
        
        # Verify calculations
        assert result['crop_type'] == "Wheat"
        assert result['area_acres'] == 5.0
        assert result['profit_margin']['net_profit'] > 0
        assert result['profit_margin']['profit_margin_percentage'] > 0
        print("\n✓ All assertions passed")
        
        # Test 3: Calculate with custom costs
        print("\n3. Testing with custom cost overrides...")
        custom_result = profit_service.calculate_profit_margin(
            crop_type="Wheat",
            state="Punjab",
            district="Ludhiana",
            area_acres=3.0,
            custom_costs={
                'seed_cost': 5000.0,
                'fertilizer_cost': 10000.0
            }
        )
        
        print(f"✓ Custom costs applied successfully")
        print(f"  Custom seed cost: ₹{custom_result['costs']['per_acre']['seed_cost']:,.2f}")
        print(f"  Custom fertilizer cost: ₹{custom_result['costs']['per_acre']['fertilizer_cost']:,.2f}")
        assert custom_result['costs']['per_acre']['seed_cost'] == 5000.0
        assert custom_result['costs']['per_acre']['fertilizer_cost'] == 10000.0
        print("✓ Custom cost assertions passed")
        
        # Test 4: Add data for comparative analysis
        print("\n4. Adding Rice data for comparative analysis...")
        rice_profitability = CropProfitability(
            crop_type="Rice",
            state="Punjab",
            district="Ludhiana",
            year=2023,
            season="kharif",
            avg_profit_per_acre=Decimal("38000.00"),
            seed_cost=Decimal("4000.00"),
            fertilizer_cost=Decimal("9000.00"),
            pesticide_cost=Decimal("3000.00"),
            labor_cost=Decimal("14000.00"),
            irrigation_cost=Decimal("4000.00"),
            equipment_cost=Decimal("1000.00"),
            other_costs=Decimal("0.00"),
            total_investment_cost=Decimal("35000.00"),
            avg_revenue_per_acre=Decimal("73000.00"),
            profit_margin=Decimal("47.95")
        )
        session.add(rice_profitability)
        
        rice_market = CropMarketData(
            crop_type="Rice",
            state="Punjab",
            district="Ludhiana",
            year=2023,
            avg_price_per_quintal=Decimal("2500.00")
        )
        session.add(rice_market)
        
        rice_yield = HistoricalYield(
            crop_type="Rice",
            state="Punjab",
            district="Ludhiana",
            year=2023,
            avg_yield_per_acre=Decimal("30.00")
        )
        session.add(rice_yield)
        session.commit()
        print("✓ Rice data added successfully")
        
        # Test 5: Comparative margin analysis
        print("\n5. Running comparative margin analysis...")
        comparison = profit_service.calculate_comparative_margins(
            crops=["Wheat", "Rice"],
            state="Punjab",
            district="Ludhiana",
            area_acres=5.0
        )
        
        print(f"✓ Comparative analysis completed")
        print(f"  Crops analyzed: {comparison['crops_analyzed']}")
        print(f"\n  Best margin crop: {comparison['best_margin']['crop']}")
        print(f"    - Margin: {comparison['best_margin']['margin_percentage']:.2f}%")
        print(f"    - Net profit: ₹{comparison['best_margin']['net_profit']:,.2f}")
        print(f"\n  Worst margin crop: {comparison['worst_margin']['crop']}")
        print(f"    - Margin: {comparison['worst_margin']['margin_percentage']:.2f}%")
        print(f"    - Net profit: ₹{comparison['worst_margin']['net_profit']:,.2f}")
        print(f"\n  Average margin: {comparison['average_margin']:.2f}%")
        
        if comparison.get('comparison_insights'):
            print(f"\n  Insights:")
            for insight in comparison['comparison_insights']:
                print(f"    - {insight}")
        
        assert comparison['crops_analyzed'] == 2
        assert comparison['best_margin']['margin_percentage'] >= comparison['worst_margin']['margin_percentage']
        print("\n✓ Comparative analysis assertions passed")
        
        # Test 6: Test profit margin percentage formula
        print("\n6. Testing profit margin calculation formula...")
        test_revenue = {
            'per_acre': {'yield_quintals': 30, 'price_per_quintal': 2000, 'revenue_per_acre': 60000},
            'total_area': {'total_yield_quintals': 30, 'total_revenue': 60000}
        }
        test_costs = {
            'per_acre': {'total_cost_per_acre': 25000},
            'total_area': {'total_costs': 25000}
        }
        
        margin_result = profit_service._calculate_margin_metrics(
            revenue=test_revenue,
            costs=test_costs,
            area_acres=1.0
        )
        
        # Net profit = 60000 - 25000 = 35000
        assert margin_result['net_profit'] == 35000
        print(f"✓ Net profit: ₹{margin_result['net_profit']:,.2f}")
        
        # Profit margin = (35000 / 60000) * 100 = 58.33%
        expected_margin = (35000 / 60000) * 100
        assert abs(margin_result['profit_margin_percentage'] - expected_margin) < 0.01
        print(f"✓ Profit margin: {margin_result['profit_margin_percentage']:.2f}%")
        
        # ROI = (35000 / 25000) * 100 = 140%
        expected_roi = (35000 / 25000) * 100
        assert abs(margin_result['roi_percentage'] - expected_roi) < 0.01
        print(f"✓ ROI: {margin_result['roi_percentage']:.2f}%")
        
        # Break-even yield = 25000 / 2000 = 12.5 quintals
        assert margin_result['break_even_yield_quintals'] == 12.5
        print(f"✓ Break-even yield: {margin_result['break_even_yield_quintals']:.2f} quintals")
        
        print("\n✓ All formula tests passed")
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    test_profit_margin_calculation()
    print("\n✓ Profit Margin Service tests completed successfully!")

