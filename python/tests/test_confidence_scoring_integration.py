"""
Integration tests for confidence scoring in crop recommendations service

Tests validate:
- Confidence scores are returned in service responses
- Confidence scores are between 0.00 and 1.00
- Confidence scores reflect data quality
- Service properly calculates confidence for different data scenarios
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.market_intelligence import (
    CropProfitability,
    HistoricalYield,
    CropMarketData,
    SeasonalTrend
)
from app.services.crop_recommendation_service import CropRecommendationService


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



@pytest.fixture(scope="function")
def db_session():
    """Create database session for testing"""
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Add test data for Punjab, Ludhiana
    # High-quality data for Wheat
    for year in range(2020, 2024):
        db.add(CropProfitability(
            crop_type='Wheat',
            variety='HD-2967',
            state='Punjab',
            district='Ludhiana',
            season='rabi',
            year=year,
            avg_profit_per_acre=50000 + (year - 2020) * 2000,
            total_investment_cost=20000,
            roi_percentage=150
        ))
        
        db.add(HistoricalYield(
            crop_type='Wheat',
            variety='HD-2967',
            state='Punjab',
            district='Ludhiana',
            season='rabi',
            year=year,
            avg_yield_per_acre=25.0,
            success_rate=88.0,
            farmer_count=500
        ))
        
        db.add(CropMarketData(
            crop_type='Wheat',
            variety='HD-2967',
            state='Punjab',
            district='Ludhiana',
            season='rabi',
            year=year,
            month=4,
            avg_price_per_quintal=2000 + (year - 2020) * 100,
            min_price=1800,
            max_price=2200,
            market_demand_score=85,
            yoy_price_change=10.0
        ))
    
    # Limited data for Mustard
    db.add(CropProfitability(
        crop_type='Mustard',
        variety='Local',
        state='Punjab',
        district='Ludhiana',
        season='rabi',
        year=2023,
        avg_profit_per_acre=35000,
        total_investment_cost=15000,
        roi_percentage=133
    ))
    
    db.add(HistoricalYield(
        crop_type='Mustard',
        variety='Local',
        state='Punjab',
        district='Ludhiana',
        season='rabi',
        year=2023,
        avg_yield_per_acre=12.0,
        success_rate=65.0,
        farmer_count=50
    ))
    
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


class TestConfidenceScoringIntegration:
    """Integration tests for confidence scoring in service"""
    
    def test_service_returns_confidence_scores(self, db_session):
        """Test that service returns confidence scores for recommendations"""
        service = CropRecommendationService(db_session)
        
        result = service.get_rag_crop_recommendations(
            state="Punjab",
            district="Ludhiana",
            season="rabi",
            top_n=3
        )
        
        # Check response structure
        assert "top_recommendations" in result
        assert len(result["top_recommendations"]) > 0
        
        # Check each recommendation has confidence score
        for crop in result["top_recommendations"]:
            assert "confidence_score" in crop
            confidence = crop["confidence_score"]
            
            # Confidence should be a dict with detailed breakdown
            assert isinstance(confidence, dict)
            assert "overall_score" in confidence
            assert "confidence_level" in confidence
            assert "component_scores" in confidence
            assert "factors" in confidence
            assert "explanation" in confidence
            
            # Validate overall score range
            overall_score = confidence["overall_score"]
            assert 0.0 <= overall_score <= 1.0
            
            # Validate confidence level
            assert confidence["confidence_level"] in [
                "Very High", "High", "Moderate", "Low", "Very Low"
            ]
            
            # Validate component scores
            components = confidence["component_scores"]
            assert "data_quality" in components
            assert "historical_accuracy" in components
            assert "market_stability" in components
            assert "prediction_reliability" in components
            
            # All components should be between 0 and their max values
            assert 0.0 <= components["data_quality"] <= 0.25
            assert 0.0 <= components["historical_accuracy"] <= 0.30
            assert 0.0 <= components["market_stability"] <= 0.25
            assert 0.0 <= components["prediction_reliability"] <= 0.20
    
    def test_high_quality_data_has_high_confidence(self, db_session):
        """Test that crops with high-quality data have higher confidence scores"""
        service = CropRecommendationService(db_session)
        
        result = service.get_rag_crop_recommendations(
            state="Punjab",
            district="Ludhiana",
            season="rabi",
            top_n=3
        )
        
        # Find Wheat (high-quality data) and Mustard (limited data)
        wheat_confidence = None
        mustard_confidence = None
        
        for crop in result["top_recommendations"]:
            confidence = crop["confidence_score"]
            score = confidence["overall_score"]
            
            if crop["crop_name"] == "Wheat":
                wheat_confidence = score
            elif crop["crop_name"] == "Mustard":
                mustard_confidence = score
        
        # Wheat should have higher confidence due to more data points
        if wheat_confidence is not None and mustard_confidence is not None:
            assert wheat_confidence > mustard_confidence
    
    def test_confidence_score_components_are_valid(self, db_session):
        """Test that confidence score components are within valid ranges"""
        service = CropRecommendationService(db_session)
        
        result = service.get_rag_crop_recommendations(
            state="Punjab",
            district="Ludhiana",
            season="rabi"
        )
        
        for crop in result["top_recommendations"]:
            confidence = crop["confidence_score"]
            
            # Check overall score
            assert 0.0 <= confidence["overall_score"] <= 1.0
            
            # Check component scores sum doesn't exceed 1.0
            components = confidence["component_scores"]
            total = sum(components.values())
            assert total <= 1.0
            
            # Check factors list exists
            assert isinstance(confidence["factors"], list)
            assert len(confidence["factors"]) > 0
    
    def test_confidence_explanation_is_meaningful(self, db_session):
        """Test that confidence explanation contains meaningful information"""
        service = CropRecommendationService(db_session)
        
        result = service.get_rag_crop_recommendations(
            state="Punjab",
            district="Ludhiana",
            season="rabi"
        )
        
        for crop in result["top_recommendations"]:
            confidence = crop["confidence_score"]
            explanation = confidence["explanation"]
            
            # Explanation should contain confidence level
            assert confidence["confidence_level"] in explanation
            
            # Explanation should be non-empty
            assert len(explanation) > 20
            
            # Factors should be descriptive
            for factor in confidence["factors"]:
                assert len(factor) > 5
    
    def test_recommendation_summary_includes_confidence(self, db_session):
        """Test that recommendation summary includes confidence information"""
        service = CropRecommendationService(db_session)
        
        result = service.get_rag_crop_recommendations(
            state="Punjab",
            district="Ludhiana",
            season="rabi"
        )
        
        assert "recommendation_summary" in result
        summary = result["recommendation_summary"]
        
        assert "top_recommendation" in summary
        top_rec = summary["top_recommendation"]
        
        assert "confidence" in top_rec
        confidence = top_rec["confidence"]
        assert 0.0 <= confidence <= 1.0
    
    def test_confidence_scores_are_consistent(self, db_session):
        """Test that confidence scores are consistent across multiple calls"""
        service = CropRecommendationService(db_session)
        
        # Make first call
        result1 = service.get_rag_crop_recommendations(
            state="Punjab",
            district="Ludhiana",
            season="rabi"
        )
        
        # Make second call
        result2 = service.get_rag_crop_recommendations(
            state="Punjab",
            district="Ludhiana",
            season="rabi"
        )
        
        # Compare confidence scores for same crops
        for i, crop1 in enumerate(result1["top_recommendations"]):
            crop2 = result2["top_recommendations"][i]
            
            conf1 = crop1["confidence_score"]
            conf2 = crop2["confidence_score"]
            
            # Scores should be identical
            assert conf1["overall_score"] == conf2["overall_score"]
    
    def test_quick_recommendations_include_confidence(self, db_session):
        """Test that quick recommendations (no rotation) include confidence scores"""
        service = CropRecommendationService(db_session)
        
        result = service.get_rag_crop_recommendations(
            state="Punjab",
            district="Ludhiana",
            season="rabi",
            include_rotation=False
        )
        
        assert "top_recommendations" in result
        for crop in result["top_recommendations"]:
            assert "confidence_score" in crop
            assert isinstance(crop["confidence_score"], dict)
            assert "overall_score" in crop["confidence_score"]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
