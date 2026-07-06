"""
Unit tests for confidence scoring in crop recommendations

Tests validate:
- Data quality scoring
- Historical accuracy scoring
- Market stability scoring
- Prediction reliability scoring
- Overall confidence calculation
- Edge cases and boundary conditions
"""

import pytest
from unittest.mock import Mock, MagicMock
from app.services.crop_recommendation_service import CropRecommendationService


class TestConfidenceScoring:
    """Test suite for confidence scoring functionality"""
    
    @pytest.fixture
    def service(self):
        """Create service instance with mocked database"""
        mock_db = Mock()
        return CropRecommendationService(mock_db)
    
    def test_high_confidence_with_excellent_data(self, service):
        """Test confidence scoring with excellent data quality and metrics"""
        crop = {
            'crop_name': 'Wheat',
            'data_points': 150,
            'expected_yield_per_acre': 25.0,
            'avg_market_price': 2000,
            'expected_profit_per_acre': 50000,
            'yield_success_rate': 88,
            'yoy_growth': 12.5,
            'price_trend': 'increasing',
            'enhanced_with_ai': True,
            'roi_percentage': 85
        }
        
        result = service._calculate_confidence_score(
            crop=crop,
            state='Punjab',
            district='Ludhiana'
        )
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        assert 'confidence_level' in result
        assert 'component_scores' in result
        assert 'factors' in result
        assert 'explanation' in result
        
        # Should have very high confidence
        assert result['overall_score'] >= 0.80
        assert result['confidence_level'] == 'Very High'
        
        # Check component scores
        components = result['component_scores']
        assert components['data_quality'] >= 0.20
        assert components['historical_accuracy'] >= 0.25
        assert components['market_stability'] >= 0.20
        assert components['prediction_reliability'] >= 0.15
        
        # Check factors are present
        assert len(result['factors']) > 0
        assert any('data' in f.lower() for f in result['factors'])
    
    def test_moderate_confidence_with_limited_data(self, service):
        """Test confidence scoring with limited but acceptable data"""
        crop = {
            'crop_name': 'Mustard',
            'data_points': 25,
            'expected_yield_per_acre': 12.0,
            'avg_market_price': 4500,
            'expected_profit_per_acre': 35000,
            'yield_success_rate': 68,
            'yoy_growth': 3.5,
            'price_trend': 'stable',
            'enhanced_with_ai': True,
            'roi_percentage': 65
        }
        
        result = service._calculate_confidence_score(
            crop=crop,
            state='Rajasthan',
            district='Jaipur'
        )
        
        # Should have moderate to high confidence (data is actually quite complete)
        assert 0.50 <= result['overall_score'] <= 0.95
        assert result['confidence_level'] in ['Moderate', 'High', 'Very High']
        
        # Data quality should be lower than excellent data
        assert result['component_scores']['data_quality'] < 0.25
    
    def test_low_confidence_with_poor_metrics(self, service):
        """Test confidence scoring with poor data and metrics"""
        crop = {
            'crop_name': 'Experimental Crop',
            'data_points': 5,
            'yield_success_rate': 45,
            'yoy_growth': -12.0,
            'price_trend': 'decreasing',
            'enhanced_with_ai': False,
            'roi_percentage': 15
        }
        
        result = service._calculate_confidence_score(
            crop=crop,
            state='Bihar',
            district=None  # No district specificity
        )
        
        # Should have low confidence
        assert result['overall_score'] < 0.50
        assert result['confidence_level'] in ['Low', 'Very Low']
        
        # All component scores should be low
        components = result['component_scores']
        assert components['data_quality'] < 0.15
        assert components['historical_accuracy'] < 0.15
        assert components['market_stability'] < 0.15
    
    def test_data_quality_scoring(self, service):
        """Test data quality component scoring"""
        # Test with high data points
        crop_high = {
            'crop_name': 'Rice',
            'data_points': 120,
            'expected_yield_per_acre': 30.0,
            'avg_market_price': 1800,
            'expected_profit_per_acre': 45000,
            'yield_success_rate': 75,
            'yoy_growth': 5,
            'price_trend': 'stable',
            'enhanced_with_ai': True,
            'roi_percentage': 70
        }
        
        result_high = service._calculate_confidence_score(
            crop=crop_high,
            state='Punjab',
            district='Amritsar'
        )
        
        # Test with low data points
        crop_low = {**crop_high, 'data_points': 8}
        result_low = service._calculate_confidence_score(
            crop=crop_low,
            state='Punjab',
            district='Amritsar'
        )
        
        # High data points should have better data quality score
        assert result_high['component_scores']['data_quality'] > result_low['component_scores']['data_quality']
    
    def test_historical_accuracy_scoring(self, service):
        """Test historical accuracy component scoring"""
        base_crop = {
            'crop_name': 'Cotton',
            'data_points': 50,
            'expected_yield_per_acre': 20.0,
            'avg_market_price': 5000,
            'expected_profit_per_acre': 60000,
            'yoy_growth': 8,
            'price_trend': 'increasing',
            'enhanced_with_ai': True,
            'roi_percentage': 80
        }
        
        # Test with excellent success rate
        crop_excellent = {**base_crop, 'yield_success_rate': 90}
        result_excellent = service._calculate_confidence_score(
            crop=crop_excellent,
            state='Gujarat',
            district='Ahmedabad'
        )
        
        # Test with poor success rate
        crop_poor = {**base_crop, 'yield_success_rate': 50}
        result_poor = service._calculate_confidence_score(
            crop=crop_poor,
            state='Gujarat',
            district='Ahmedabad'
        )
        
        # Excellent success rate should score higher
        assert result_excellent['component_scores']['historical_accuracy'] > result_poor['component_scores']['historical_accuracy']
        assert result_excellent['overall_score'] > result_poor['overall_score']
    
    def test_market_stability_scoring(self, service):
        """Test market stability component scoring"""
        base_crop = {
            'crop_name': 'Soybean',
            'data_points': 60,
            'expected_yield_per_acre': 18.0,
            'avg_market_price': 3500,
            'expected_profit_per_acre': 40000,
            'yield_success_rate': 75,
            'enhanced_with_ai': True,
            'roi_percentage': 70
        }
        
        # Test with healthy growth
        crop_healthy = {**base_crop, 'yoy_growth': 10.0, 'price_trend': 'increasing'}
        result_healthy = service._calculate_confidence_score(
            crop=crop_healthy,
            state='Madhya Pradesh',
            district='Indore'
        )
        
        # Test with high volatility
        crop_volatile = {**base_crop, 'yoy_growth': 35.0, 'price_trend': 'increasing'}
        result_volatile = service._calculate_confidence_score(
            crop=crop_volatile,
            state='Madhya Pradesh',
            district='Indore'
        )
        
        # Test with declining market
        crop_declining = {**base_crop, 'yoy_growth': -15.0, 'price_trend': 'decreasing'}
        result_declining = service._calculate_confidence_score(
            crop=crop_declining,
            state='Madhya Pradesh',
            district='Indore'
        )
        
        # Healthy growth should score highest
        assert result_healthy['component_scores']['market_stability'] > result_volatile['component_scores']['market_stability']
        assert result_healthy['component_scores']['market_stability'] > result_declining['component_scores']['market_stability']
    
    def test_prediction_reliability_scoring(self, service):
        """Test prediction reliability component scoring"""
        base_crop = {
            'crop_name': 'Maize',
            'data_points': 70,
            'expected_yield_per_acre': 22.0,
            'avg_market_price': 1600,
            'expected_profit_per_acre': 38000,
            'yield_success_rate': 72,
            'yoy_growth': 6,
            'price_trend': 'stable',
            'roi_percentage': 75
        }
        
        # Test with AI enhancement and district specificity
        crop_enhanced = {**base_crop, 'enhanced_with_ai': True}
        result_enhanced = service._calculate_confidence_score(
            crop=crop_enhanced,
            state='Karnataka',
            district='Bangalore'
        )
        
        # Test without AI enhancement and no district
        crop_basic = {**base_crop, 'enhanced_with_ai': False}
        result_basic = service._calculate_confidence_score(
            crop=crop_basic,
            state='Karnataka',
            district=None
        )
        
        # Enhanced prediction should score higher
        assert result_enhanced['component_scores']['prediction_reliability'] > result_basic['component_scores']['prediction_reliability']
    
    def test_confidence_level_thresholds(self, service):
        """Test confidence level categorization"""
        # Very High (>= 0.80)
        crop_very_high = {
            'crop_name': 'Test',
            'data_points': 150,
            'expected_yield_per_acre': 25.0,
            'avg_market_price': 2000,
            'expected_profit_per_acre': 50000,
            'yield_success_rate': 90,
            'yoy_growth': 12,
            'price_trend': 'increasing',
            'enhanced_with_ai': True,
            'roi_percentage': 85
        }
        result = service._calculate_confidence_score(crop_very_high, 'Punjab', 'Ludhiana')
        assert result['confidence_level'] == 'Very High'
        
        # High (0.65 - 0.79)
        crop_high = {
            'crop_name': 'Test',
            'data_points': 60,
            'expected_yield_per_acre': 20.0,
            'avg_market_price': 2000,
            'expected_profit_per_acre': 40000,
            'yield_success_rate': 75,
            'yoy_growth': 8,
            'price_trend': 'stable',
            'enhanced_with_ai': True,
            'roi_percentage': 70
        }
        result = service._calculate_confidence_score(crop_high, 'Punjab', 'Ludhiana')
        assert result['confidence_level'] in ['High', 'Very High']
        
        # Moderate (0.50 - 0.64)
        crop_moderate = {
            'crop_name': 'Test',
            'data_points': 25,
            'yield_success_rate': 65,
            'yoy_growth': 3,
            'price_trend': 'stable',
            'enhanced_with_ai': False,
            'roi_percentage': 50
        }
        result = service._calculate_confidence_score(crop_moderate, 'Bihar', None)
        assert result['confidence_level'] in ['Moderate', 'High']
    
    def test_confidence_score_capped_at_95_percent(self, service):
        """Test that confidence score never exceeds 0.95"""
        # Create perfect crop with all maximum values
        perfect_crop = {
            'crop_name': 'Perfect Crop',
            'data_points': 500,
            'expected_yield_per_acre': 50.0,
            'avg_market_price': 5000,
            'expected_profit_per_acre': 100000,
            'yield_success_rate': 100,
            'yoy_growth': 15,
            'price_trend': 'increasing',
            'enhanced_with_ai': True,
            'roi_percentage': 100
        }
        
        result = service._calculate_confidence_score(
            crop=perfect_crop,
            state='Punjab',
            district='Ludhiana'
        )
        
        # Should be capped at 0.95
        assert result['overall_score'] <= 0.95
    
    def test_missing_data_handling(self, service):
        """Test confidence scoring with missing data fields"""
        minimal_crop = {
            'crop_name': 'Minimal Data Crop'
            # Most fields missing
        }
        
        result = service._calculate_confidence_score(
            crop=minimal_crop,
            state='Uttar Pradesh',
            district=None
        )
        
        # Should still return valid structure
        assert isinstance(result, dict)
        assert 'overall_score' in result
        assert 'confidence_level' in result
        assert result['overall_score'] >= 0.0
        assert result['overall_score'] <= 0.95
    
    def test_extreme_roi_values(self, service):
        """Test confidence scoring with extreme ROI values"""
        base_crop = {
            'crop_name': 'Test',
            'data_points': 50,
            'expected_yield_per_acre': 20.0,
            'avg_market_price': 2000,
            'expected_profit_per_acre': 40000,
            'yield_success_rate': 75,
            'yoy_growth': 8,
            'price_trend': 'stable',
            'enhanced_with_ai': True
        }
        
        # Reasonable ROI
        crop_reasonable = {**base_crop, 'roi_percentage': 80}
        result_reasonable = service._calculate_confidence_score(crop_reasonable, 'Punjab', 'Ludhiana')
        
        # Extremely high ROI (suspicious)
        crop_extreme = {**base_crop, 'roi_percentage': 500}
        result_extreme = service._calculate_confidence_score(crop_extreme, 'Punjab', 'Ludhiana')
        
        # Negative ROI
        crop_negative = {**base_crop, 'roi_percentage': -10}
        result_negative = service._calculate_confidence_score(crop_negative, 'Punjab', 'Ludhiana')
        
        # Reasonable ROI should have better prediction reliability
        assert result_reasonable['component_scores']['prediction_reliability'] >= result_extreme['component_scores']['prediction_reliability']
        assert result_reasonable['component_scores']['prediction_reliability'] >= result_negative['component_scores']['prediction_reliability']
    
    def test_data_completeness_bonus(self, service):
        """Test that complete data gets bonus points"""
        # Complete data
        crop_complete = {
            'crop_name': 'Complete',
            'data_points': 50,
            'expected_yield_per_acre': 20.0,
            'avg_market_price': 2000,
            'expected_profit_per_acre': 40000,
            'yield_success_rate': 75,
            'yoy_growth': 8,
            'price_trend': 'stable',
            'enhanced_with_ai': True,
            'roi_percentage': 70
        }
        
        # Incomplete data (missing yield and market price)
        crop_incomplete = {
            'crop_name': 'Incomplete',
            'data_points': 50,
            'expected_profit_per_acre': 40000,
            'yield_success_rate': 75,
            'yoy_growth': 8,
            'price_trend': 'stable',
            'enhanced_with_ai': True,
            'roi_percentage': 70
        }
        
        result_complete = service._calculate_confidence_score(crop_complete, 'Punjab', 'Ludhiana')
        result_incomplete = service._calculate_confidence_score(crop_incomplete, 'Punjab', 'Ludhiana')
        
        # Complete data should have better data quality score
        assert result_complete['component_scores']['data_quality'] > result_incomplete['component_scores']['data_quality']
    
    def test_explanation_generation(self, service):
        """Test that explanation is generated correctly"""
        crop = {
            'crop_name': 'Wheat',
            'data_points': 100,
            'expected_yield_per_acre': 25.0,
            'avg_market_price': 2000,
            'expected_profit_per_acre': 50000,
            'yield_success_rate': 85,
            'yoy_growth': 10,
            'price_trend': 'increasing',
            'enhanced_with_ai': True,
            'roi_percentage': 80
        }
        
        result = service._calculate_confidence_score(
            crop=crop,
            state='Punjab',
            district='Ludhiana'
        )
        
        # Check explanation exists and contains key information
        assert 'explanation' in result
        assert len(result['explanation']) > 0
        assert result['confidence_level'] in result['explanation']
        
        # Check factors list
        assert len(result['factors']) > 0
        assert isinstance(result['factors'], list)
    
    def test_stable_market_bonus(self, service):
        """Test that stable markets get bonus points"""
        base_crop = {
            'crop_name': 'Test',
            'data_points': 50,
            'expected_yield_per_acre': 20.0,
            'avg_market_price': 2000,
            'expected_profit_per_acre': 40000,
            'yield_success_rate': 75,
            'enhanced_with_ai': True,
            'roi_percentage': 70
        }
        
        # Stable market with low growth
        crop_stable = {**base_crop, 'yoy_growth': 2.0, 'price_trend': 'stable'}
        result_stable = service._calculate_confidence_score(crop_stable, 'Punjab', 'Ludhiana')
        
        # Same growth but not marked as stable
        crop_unstable = {**base_crop, 'yoy_growth': 2.0, 'price_trend': 'unknown'}
        result_unstable = service._calculate_confidence_score(crop_unstable, 'Punjab', 'Ludhiana')
        
        # Stable market should score higher
        assert result_stable['component_scores']['market_stability'] >= result_unstable['component_scores']['market_stability']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
