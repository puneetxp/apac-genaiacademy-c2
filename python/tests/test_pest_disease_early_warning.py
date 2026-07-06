"""
Tests for Pest and Disease Early Warning System
Task 25.2: Build pest and disease early warning system

Validates: Requirements AC10 (Phase 6 - Required)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from app.services.pest_disease_service import (
    PestDiseaseService,
    PEST_DISEASE_THRESHOLDS,
    PEST_DISEASE_MANAGEMENT
)


@pytest.fixture
def mock_db():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def pest_disease_service(mock_db):
    """Create pest disease service instance"""
    return PestDiseaseService(mock_db)


@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing"""
    return {
        'temperature': 25,
        'humidity': 75,
        'rainfall': 10
    }


class TestPestDiseaseRiskDetection:
    """Test pest and disease risk detection"""
    
    @pytest.mark.asyncio
    async def test_detect_aphid_risk(self, pest_disease_service):
        """Test detection of aphid infestation risk"""
        weather_data = {
            'temperature': 25,  # Within 20-30 range
            'humidity': 65,     # Above 60
            'rainfall': 0
        }
        
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1,
            weather_data=weather_data,
            current_stage='vegetative'
        )
        
        # Should detect aphid risk
        aphid_risks = [r for r in risks if r['pest_disease'] == 'aphids']
        assert len(aphid_risks) > 0
        assert aphid_risks[0]['severity'] == 'medium'
        assert 'management' in aphid_risks[0]
    
    @pytest.mark.asyncio
    async def test_detect_fungal_disease_risk(self, pest_disease_service):
        """Test detection of fungal disease risk"""
        weather_data = {
            'temperature': 22,  # Within 15-28 range
            'humidity': 85,     # Above 80
            'rainfall': 8       # Above 5mm
        }
        
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1,
            weather_data=weather_data,
            current_stage='flowering'
        )
        
        # Should detect fungal disease risk
        fungal_risks = [r for r in risks if r['pest_disease'] == 'fungal_diseases']
        assert len(fungal_risks) > 0
        assert fungal_risks[0]['severity'] == 'high'
    
    @pytest.mark.asyncio
    async def test_no_risk_outside_temperature_range(self, pest_disease_service):
        """Test no risk detected when temperature is outside range"""
        weather_data = {
            'temperature': 10,  # Too cold for most pests
            'humidity': 80,
            'rainfall': 5
        }
        
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1,
            weather_data=weather_data,
            current_stage='vegetative'
        )
        
        # Should detect no or minimal risks
        assert len(risks) == 0 or all(r['severity'] == 'low' for r in risks)
    
    @pytest.mark.asyncio
    async def test_stage_specific_risk_detection(self, pest_disease_service):
        """Test that risks are only detected for relevant crop stages"""
        weather_data = {
            'temperature': 25,
            'humidity': 70,
            'rainfall': 0
        }
        
        # Check germination stage (should have fewer risks)
        germination_risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1,
            weather_data=weather_data,
            current_stage='germination'
        )
        
        # Check vegetative stage (should have more risks)
        vegetative_risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1,
            weather_data=weather_data,
            current_stage='vegetative'
        )
        
        # Vegetative stage should have more risks than germination
        assert len(vegetative_risks) >= len(germination_risks)
    
    @pytest.mark.asyncio
    async def test_multiple_risks_detected(self, pest_disease_service):
        """Test detection of multiple simultaneous risks"""
        weather_data = {
            'temperature': 26,  # Suitable for multiple pests
            'humidity': 75,     # High humidity
            'rainfall': 6       # Some rainfall
        }
        
        risks = await pest_disease_service.check_pest_disease_risk(
            crop_id=1,
            weather_data=weather_data,
            current_stage='vegetative'
        )
        
        # Should detect multiple risks
        assert len(risks) >= 2
        
        # Each risk should have required fields
        for risk in risks:
            assert 'pest_disease' in risk
            assert 'severity' in risk
            assert 'description' in risk
            assert 'current_conditions' in risk
            assert 'management' in risk
            assert 'detected_at' in risk


class TestManagementRecommendations:
    """Test pest and disease management recommendations"""
    
    @pytest.mark.asyncio
    async def test_get_organic_recommendations(self, pest_disease_service):
        """Test retrieval of organic management recommendations"""
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease='aphids',
            preference='organic'
        )
        
        assert 'organic_options' in recommendations
        assert len(recommendations['organic_options']) > 0
        assert 'neem oil' in recommendations['organic_options'][0].lower()
        assert 'chemical_options' not in recommendations
    
    @pytest.mark.asyncio
    async def test_get_chemical_recommendations(self, pest_disease_service):
        """Test retrieval of chemical management recommendations"""
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease='fungal_diseases',
            preference='chemical'
        )
        
        assert 'chemical_options' in recommendations
        assert len(recommendations['chemical_options']) > 0
        assert 'organic_options' not in recommendations
    
    @pytest.mark.asyncio
    async def test_get_both_recommendations(self, pest_disease_service):
        """Test retrieval of both organic and chemical recommendations"""
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease='stem_borer',
            preference='both'
        )
        
        assert 'organic_options' in recommendations
        assert 'chemical_options' in recommendations
        assert len(recommendations['organic_options']) > 0
        assert len(recommendations['chemical_options']) > 0
    
    @pytest.mark.asyncio
    async def test_recommendations_include_timing(self, pest_disease_service):
        """Test that recommendations include application timing"""
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease='whitefly',
            preference='both'
        )
        
        assert 'timing' in recommendations
        assert len(recommendations['timing']) > 0
        assert 'prevention' in recommendations
        assert len(recommendations['prevention']) > 0
    
    @pytest.mark.asyncio
    async def test_invalid_pest_disease(self, pest_disease_service):
        """Test handling of invalid pest/disease name"""
        recommendations = await pest_disease_service.get_management_recommendations(
            pest_disease='invalid_pest',
            preference='both'
        )
        
        assert 'error' in recommendations


class TestCropSpecificRisks:
    """Test crop-specific risk information"""
    
    @pytest.mark.asyncio
    async def test_get_vegetative_stage_risks(self, pest_disease_service):
        """Test retrieval of risks for vegetative stage"""
        risks = await pest_disease_service.get_crop_specific_risks(
            crop_name='rice',
            current_stage='vegetative'
        )
        
        assert len(risks) > 0
        
        # All risks should be relevant to vegetative stage
        for risk in risks:
            assert 'vegetative' in risk['risk_stages']
    
    @pytest.mark.asyncio
    async def test_get_flowering_stage_risks(self, pest_disease_service):
        """Test retrieval of risks for flowering stage"""
        risks = await pest_disease_service.get_crop_specific_risks(
            crop_name='tomato',
            current_stage='flowering'
        )
        
        assert len(risks) > 0
        
        # All risks should be relevant to flowering stage
        for risk in risks:
            assert 'flowering' in risk['risk_stages']
    
    @pytest.mark.asyncio
    async def test_risk_includes_management_info(self, pest_disease_service):
        """Test that crop-specific risks include management information"""
        risks = await pest_disease_service.get_crop_specific_risks(
            crop_name='wheat',
            current_stage='vegetative'
        )
        
        for risk in risks:
            assert 'pest_disease' in risk
            assert 'severity' in risk
            assert 'description' in risk
            assert 'management' in risk
            
            # Management should have organic and chemical options
            management = risk['management']
            assert 'organic' in management or 'chemical' in management


class TestPreventionGuidance:
    """Test disease prevention guidance"""
    
    @pytest.mark.asyncio
    async def test_get_prevention_guidance(self, pest_disease_service):
        """Test retrieval of prevention guidance for crop stage"""
        guidance = await pest_disease_service.get_prevention_guidance(
            crop_id=1,
            current_stage='vegetative'
        )
        
        assert 'crop_id' in guidance
        assert 'current_stage' in guidance
        assert 'relevant_risks' in guidance
        assert 'prevention_measures' in guidance
        assert 'timing_instructions' in guidance
        assert 'general_guidance' in guidance
    
    @pytest.mark.asyncio
    async def test_prevention_measures_not_empty(self, pest_disease_service):
        """Test that prevention measures are provided"""
        guidance = await pest_disease_service.get_prevention_guidance(
            crop_id=1,
            current_stage='flowering'
        )
        
        assert len(guidance['prevention_measures']) > 0
        assert len(guidance['general_guidance']) > 0
    
    @pytest.mark.asyncio
    async def test_timing_instructions_provided(self, pest_disease_service):
        """Test that timing instructions are provided"""
        guidance = await pest_disease_service.get_prevention_guidance(
            crop_id=1,
            current_stage='vegetative'
        )
        
        # Should have timing instructions for relevant risks
        if len(guidance['relevant_risks']) > 0:
            assert len(guidance['timing_instructions']) > 0


class TestAlertSystem:
    """Test pest/disease alert system"""
    
    @pytest.mark.asyncio
    async def test_send_pest_disease_alert(self, pest_disease_service):
        """Test sending pest/disease alert to farmer"""
        risk = {
            'pest_disease': 'aphids',
            'severity': 'high',
            'description': 'Aphid infestation risk',
            'management': PEST_DISEASE_MANAGEMENT['aphids']
        }
        
        with patch.object(pest_disease_service.notification_service, 'send_strategy_reminder') as mock_send:
            mock_send.return_value = {'success': True}
            
            result = await pest_disease_service.send_pest_disease_alert(
                crop_id=1,
                farmer_phone='+919876543210',
                farmer_email='farmer@example.com',
                farmer_name='Test Farmer',
                crop_name='Rice',
                risk=risk
            )
            
            assert result['success'] is True
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_alert_includes_action_items(self, pest_disease_service):
        """Test that alerts include actionable recommendations"""
        risk = {
            'pest_disease': 'fungal_diseases',
            'severity': 'high',
            'description': 'Fungal disease risk',
            'management': PEST_DISEASE_MANAGEMENT['fungal_diseases']
        }
        
        with patch.object(pest_disease_service.notification_service, 'send_strategy_reminder') as mock_send:
            mock_send.return_value = {'success': True}
            
            await pest_disease_service.send_pest_disease_alert(
                crop_id=1,
                farmer_phone='+919876543210',
                farmer_email='farmer@example.com',
                farmer_name='Test Farmer',
                crop_name='Wheat',
                risk=risk
            )
            
            # Check that action items were included in the call
            call_args = mock_send.call_args
            assert 'action_items' in call_args.kwargs
            assert len(call_args.kwargs['action_items']) > 0


class TestDataIntegrity:
    """Test data integrity and completeness"""
    
    def test_all_pests_have_management_data(self):
        """Test that all pests in thresholds have management data"""
        for pest_disease in PEST_DISEASE_THRESHOLDS.keys():
            assert pest_disease in PEST_DISEASE_MANAGEMENT, \
                f"Missing management data for {pest_disease}"
    
    def test_management_data_completeness(self):
        """Test that management data has required fields"""
        required_fields = ['organic', 'chemical', 'timing', 'prevention']
        
        for pest_disease, management in PEST_DISEASE_MANAGEMENT.items():
            for field in required_fields:
                assert field in management, \
                    f"Missing {field} in management data for {pest_disease}"
                assert len(management[field]) > 0, \
                    f"Empty {field} in management data for {pest_disease}"
    
    def test_threshold_data_completeness(self):
        """Test that threshold data has required fields"""
        required_fields = ['temp_min', 'temp_max', 'humidity_min', 'risk_stages', 'severity', 'description']
        
        for pest_disease, thresholds in PEST_DISEASE_THRESHOLDS.items():
            for field in required_fields:
                assert field in thresholds, \
                    f"Missing {field} in threshold data for {pest_disease}"
    
    def test_severity_levels_valid(self):
        """Test that severity levels are valid"""
        valid_severities = ['low', 'medium', 'high']
        
        for pest_disease, thresholds in PEST_DISEASE_THRESHOLDS.items():
            severity = thresholds['severity']
            assert severity in valid_severities, \
                f"Invalid severity '{severity}' for {pest_disease}"
    
    def test_risk_stages_valid(self):
        """Test that risk stages are valid"""
        valid_stages = ['germination', 'vegetative', 'flowering', 'maturation']
        
        for pest_disease, thresholds in PEST_DISEASE_THRESHOLDS.items():
            risk_stages = thresholds['risk_stages']
            for stage in risk_stages:
                assert stage in valid_stages, \
                    f"Invalid stage '{stage}' for {pest_disease}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
