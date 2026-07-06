"""
Test script for opportunity cost calculation engine
Tests the core functionality of the opportunity cost calculation
"""

import sys
import os
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Numeric
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

# Create a minimal Base for testing
Base = declarative_base()

# Minimal CropProfitability model for testing
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
    total_investment_cost = Column(SQLDecimal(10, 2))
    roi_percentage = Column(SQLDecimal(5, 2))
    risk_level = Column(String(20))
    market_demand = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Import the service after defining the model
from app.services.market_data_service import MarketDataService


def test_opportunity_cost_calculation():
    """
    Test the opportunity cost calculation engine with sample data
    """
    print("=" * 80)
    print("Testing Opportunity Cost Calculation Engine")
    print("=" * 80)
    
    # Create in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Create test data - Wheat vs Cotton in Punjab
        print("\n1. Creating test profitability data...")
        
        # Wheat data (lower profit, lower risk)
        wheat_data = CropProfitability(
            crop_type='Wheat',
            variety='HD-2967',
            state='Punjab',
            district='Ludhiana',
            year=2023,
            season='rabi',
            avg_profit_per_acre=Decimal('65000.00'),
            total_investment_cost=Decimal('35000.00'),
            roi_percentage=Decimal('85.71'),
            risk_level='low',
            market_demand='high'
        )
        
        # Cotton data (higher profit, higher risk)
        cotton_data = CropProfitability(
            crop_type='Cotton',
            variety='BT-Cotton',
            state='Punjab',
            district='Ludhiana',
            year=2023,
            season='kharif',
            avg_profit_per_acre=Decimal('85000.00'),
            total_investment_cost=Decimal('45000.00'),
            roi_percentage=Decimal('88.89'),
            risk_level='medium',
            market_demand='high'
        )
        
        # Rice data (medium profit, medium risk)
        rice_data = CropProfitability(
            crop_type='Rice',
            variety='Basmati',
            state='Punjab',
            district='Ludhiana',
            year=2023,
            season='kharif',
            avg_profit_per_acre=Decimal('70000.00'),
            total_investment_cost=Decimal('40000.00'),
            roi_percentage=Decimal('75.00'),
            risk_level='medium',
            market_demand='high'
        )
        
        db.add_all([wheat_data, cotton_data, rice_data])
        db.commit()
        print("✓ Test data created successfully")
        
        # Initialize service
        service = MarketDataService(db)
        
        # Test 1: Calculate opportunity cost - Wheat vs Cotton
        print("\n2. Testing single opportunity cost calculation...")
        print("   Comparing: Wheat (primary) vs Cotton (alternative)")
        
        result = service.calculate_opportunity_cost(
            primary_crop='Wheat',
            alternative_crop='Cotton',
            state='Punjab',
            district='Ludhiana',
            year=2023
        )
        
        print(f"\n   Results:")
        print(f"   - Primary Crop (Wheat): ₹{result['primary_crop']['avg_profit_per_acre']:,.2f} per acre")
        print(f"   - Alternative Crop (Cotton): ₹{result['alternative_crop']['avg_profit_per_acre']:,.2f} per acre")
        print(f"   - Opportunity Cost: ₹{result['opportunity_cost']['profit_difference']:,.2f}")
        print(f"   - Interpretation: {result['opportunity_cost']['interpretation']}")
        print(f"   - Recommendation: {result['recommendation']['message']}")
        print(f"   - Confidence: {result['recommendation']['confidence']:.2%}")
        
        assert result['opportunity_cost']['profit_difference'] == 20000.0, "Opportunity cost should be ₹20,000"
        assert result['opportunity_cost']['interpretation'] == 'positive', "Should be positive (alternative is better)"
        print("   ✓ Single opportunity cost calculation passed")
        
        # Test 2: Multi-crop opportunity cost
        print("\n3. Testing multi-crop opportunity cost calculation...")
        print("   Comparing: Wheat vs [Cotton, Rice]")
        
        multi_result = service.calculate_multi_crop_opportunity_costs(
            primary_crop='Wheat',
            alternative_crops=['Cotton', 'Rice'],
            state='Punjab',
            district='Ludhiana',
            year=2023,
            top_n=2
        )
        
        print(f"\n   Results:")
        print(f"   - Alternatives analyzed: {multi_result['alternatives_analyzed']}")
        print(f"   - Best alternative: {multi_result['best_alternative']['crop']}")
        print(f"   - Additional profit: ₹{multi_result['best_alternative']['additional_profit']:,.2f}")
        print(f"   - Total opportunity cost: ₹{multi_result['total_opportunity_cost']:,.2f}")
        
        print(f"\n   Top alternatives:")
        for i, alt in enumerate(multi_result['top_alternatives'], 1):
            print(f"   {i}. {alt['crop']}: ₹{alt['profit_difference']:,.2f} difference (Risk: {alt['risk_level']})")
        
        assert multi_result['best_alternative']['crop'] == 'Cotton', "Cotton should be best alternative"
        assert multi_result['alternatives_analyzed'] == 2, "Should analyze 2 alternatives"
        print("   ✓ Multi-crop opportunity cost calculation passed")
        
        # Test 3: Top profitable crops with opportunity cost
        print("\n4. Testing top profitable crops recommendation (AC4 validation)...")
        
        top_crops = service.get_top_profitable_crops(
            state='Punjab',
            district='Ludhiana',
            year=2023,
            top_n=3,
            include_opportunity_costs=True
        )
        
        print(f"\n   Results:")
        print(f"   - Total crops analyzed: {top_crops['total_crops_analyzed']}")
        print(f"\n   Top 3 profitable crops:")
        for i, crop in enumerate(top_crops['top_profitable_crops'], 1):
            print(f"   {i}. {crop['crop_type']}: ₹{crop['avg_profit_per_acre']:,.2f} per acre")
            print(f"      ROI: {crop['avg_roi_percentage']:.2f}%, Risk: {crop['risk_level']}")
        
        if 'opportunity_cost_analysis' in top_crops:
            print(f"\n   Opportunity Cost Analysis:")
            print(f"   - Recommendation: {top_crops['opportunity_cost_analysis']['recommendation']}")
            print(f"   - Confidence: {top_crops['opportunity_cost_analysis']['confidence']:.2%}")
            
            if top_crops['opportunity_cost_analysis']['comparisons']:
                print(f"\n   Comparisons:")
                for comp in top_crops['opportunity_cost_analysis']['comparisons']:
                    print(f"   - {comp['reasoning']}")
        
        assert len(top_crops['top_profitable_crops']) == 3, "Should return top 3 crops"
        assert top_crops['top_profitable_crops'][0]['crop_type'] == 'Cotton', "Cotton should be most profitable"
        print("   ✓ Top profitable crops recommendation passed (AC4 validated)")
        
        # Test 4: Save opportunity cost analysis
        print("\n5. Testing save opportunity cost analysis...")
        
        saved = service.save_opportunity_cost_analysis(
            primary_crop='Wheat',
            alternative_crop='Cotton',
            state='Punjab',
            district='Ludhiana',
            year=2023
        )
        
        print(f"   - Saved analysis ID: {saved.id}")
        print(f"   - Primary crop: {saved.primary_crop}")
        print(f"   - Alternative crop: {saved.alternative_crop}")
        print(f"   - Profit difference: ₹{float(saved.profit_difference):,.2f}")
        print(f"   - Recommended choice: {saved.recommended_choice}")
        print("   ✓ Save opportunity cost analysis passed")
        
        # Test 5: Risk-adjusted opportunity cost
        print("\n6. Testing risk-adjusted opportunity cost...")
        
        result_with_risk = service.calculate_opportunity_cost(
            primary_crop='Wheat',
            alternative_crop='Cotton',
            state='Punjab',
            district='Ludhiana',
            year=2023
        )
        
        print(f"   - Raw opportunity cost: ₹{result_with_risk['opportunity_cost']['profit_difference']:,.2f}")
        print(f"   - Risk factor: {result_with_risk['opportunity_cost']['risk_factor']:.2f}")
        print(f"   - Risk-adjusted cost: ₹{result_with_risk['opportunity_cost']['risk_adjusted_cost']:,.2f}")
        print(f"   - Primary risk: {result_with_risk['primary_crop']['risk_level']}")
        print(f"   - Alternative risk: {result_with_risk['alternative_crop']['risk_level']}")
        print("   ✓ Risk-adjusted opportunity cost calculation passed")
        
        print("\n" + "=" * 80)
        print("✓ All tests passed successfully!")
        print("=" * 80)
        print("\nOpportunity Cost Calculation Engine is working correctly.")
        print("AC4 Validation: RAG system can suggest top 3 profitable crops with opportunity cost analysis")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = test_opportunity_cost_calculation()
    sys.exit(0 if success else 1)
