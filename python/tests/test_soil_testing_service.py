"""
Unit tests for Soil Testing Service
Tests soil health score calculation, recommendations, and data parsing

Task 22.1: Integrate with soil testing laboratories
"""

import pytest
from app.services.soil_testing_service import SoilTestingService


@pytest.fixture
def soil_testing_service():
    """Fixture for soil testing service"""
    return SoilTestingService()


@pytest.fixture
def optimal_soil_data():
    """Fixture for optimal soil test data"""
    return {
        'ph_level': 6.5,
        'organic_carbon_percent': 0.6,
        'nitrogen_kg_per_ha': 400,
        'phosphorus_kg_per_ha': 35,
        'potassium_kg_per_ha': 350,
        'electrical_conductivity': 0.5,
        'zinc_ppm': 0.8,
        'iron_ppm': 6.0,
        'manganese_ppm': 3.0,
        'copper_ppm': 0.3,
        'boron_ppm': 0.7
    }


@pytest.fixture
def poor_soil_data():
    """Fixture for poor soil test data"""
    return {
        'ph_level': 5.0,
        'organic_carbon_percent': 0.2,
        'nitrogen_kg_per_ha': 150,
        'phosphorus_kg_per_ha': 10,
        'potassium_kg_per_ha': 150,
        'electrical_conductivity': 2.5,
        'zinc_ppm': 0.3
    }


class TestSoilHealthScoreCalculation:
    """Test soil health score calculation algorithm"""
    
    def test_optimal_soil_gets_high_score(self, soil_testing_service, optimal_soil_data):
        """Test that optimal soil parameters result in high health score"""
        score = soil_testing_service.calculate_soil_health_score(optimal_soil_data)
        
        assert score >= 85, f"Expected score >= 85 for optimal soil, got {score}"
        assert score <= 100, f"Score should not exceed 100, got {score}"
    
    def test_poor_soil_gets_low_score(self, soil_testing_service, poor_soil_data):
        """Test that poor soil parameters result in low health score"""
        score = soil_testing_service.calculate_soil_health_score(poor_soil_data)
        
        assert score < 60, f"Expected score < 60 for poor soil, got {score}"
        assert score >= 0, f"Score should not be negative, got {score}"
    
    def test_empty_soil_data_returns_zero(self, soil_testing_service):
        """Test that empty soil data returns zero score"""
        score = soil_testing_service.calculate_soil_health_score({})
        
        assert score == 0.0, f"Expected score 0.0 for empty data, got {score}"
    
    def test_partial_soil_data_calculates_score(self, soil_testing_service):
        """Test that partial soil data still calculates a score"""
        partial_data = {
            'ph_level': 6.5,
            'nitrogen_kg_per_ha': 400,
            'phosphorus_kg_per_ha': 35
        }
        
        score = soil_testing_service.calculate_soil_health_score(partial_data)
        
        assert 0 <= score <= 100, f"Score should be between 0-100, got {score}"
        assert score > 0, "Score should be positive with valid parameters"
    
    def test_acidic_soil_reduces_score(self, soil_testing_service):
        """Test that acidic soil (low pH) reduces health score"""
        acidic_soil = {
            'ph_level': 4.5,
            'nitrogen_kg_per_ha': 400,
            'phosphorus_kg_per_ha': 35,
            'potassium_kg_per_ha': 350
        }
        
        neutral_soil = {
            'ph_level': 6.5,
            'nitrogen_kg_per_ha': 400,
            'phosphorus_kg_per_ha': 35,
            'potassium_kg_per_ha': 350
        }
        
        acidic_score = soil_testing_service.calculate_soil_health_score(acidic_soil)
        neutral_score = soil_testing_service.calculate_soil_health_score(neutral_soil)
        
        assert acidic_score < neutral_score, "Acidic soil should have lower score than neutral soil"
    
    def test_alkaline_soil_reduces_score(self, soil_testing_service):
        """Test that alkaline soil (high pH) reduces health score"""
        alkaline_soil = {
            'ph_level': 9.0,
            'nitrogen_kg_per_ha': 400,
            'phosphorus_kg_per_ha': 35,
            'potassium_kg_per_ha': 350
        }
        
        neutral_soil = {
            'ph_level': 6.5,
            'nitrogen_kg_per_ha': 400,
            'phosphorus_kg_per_ha': 35,
            'potassium_kg_per_ha': 350
        }
        
        alkaline_score = soil_testing_service.calculate_soil_health_score(alkaline_soil)
        neutral_score = soil_testing_service.calculate_soil_health_score(neutral_soil)
        
        assert alkaline_score < neutral_score, "Alkaline soil should have lower score than neutral soil"
    
    def test_low_organic_carbon_reduces_score(self, soil_testing_service):
        """Test that low organic carbon reduces health score"""
        low_oc_soil = {
            'organic_carbon_percent': 0.2,
            'ph_level': 6.5,
            'nitrogen_kg_per_ha': 400
        }
        
        good_oc_soil = {
            'organic_carbon_percent': 0.6,
            'ph_level': 6.5,
            'nitrogen_kg_per_ha': 400
        }
        
        low_score = soil_testing_service.calculate_soil_health_score(low_oc_soil)
        good_score = soil_testing_service.calculate_soil_health_score(good_oc_soil)
        
        assert low_score < good_score, "Low organic carbon should reduce score"
    
    def test_high_salinity_reduces_score(self, soil_testing_service):
        """Test that high electrical conductivity (salinity) reduces score"""
        saline_soil = {
            'electrical_conductivity': 3.0,
            'ph_level': 6.5,
            'nitrogen_kg_per_ha': 400
        }
        
        normal_soil = {
            'electrical_conductivity': 0.5,
            'ph_level': 6.5,
            'nitrogen_kg_per_ha': 400
        }
        
        saline_score = soil_testing_service.calculate_soil_health_score(saline_soil)
        normal_score = soil_testing_service.calculate_soil_health_score(normal_soil)
        
        assert saline_score < normal_score, "High salinity should reduce score"
    
    def test_score_is_deterministic(self, soil_testing_service, optimal_soil_data):
        """Test that same input produces same score (deterministic)"""
        score1 = soil_testing_service.calculate_soil_health_score(optimal_soil_data)
        score2 = soil_testing_service.calculate_soil_health_score(optimal_soil_data)
        
        assert score1 == score2, "Score calculation should be deterministic"


class TestSoilImprovementRecommendations:
    """Test soil improvement recommendation generation"""
    
    def test_acidic_soil_gets_lime_recommendation(self, soil_testing_service):
        """Test that acidic soil gets lime application recommendation"""
        acidic_soil = {
            'ph_level': 5.0,
            'nitrogen_kg_per_ha': 400
        }
        
        score = soil_testing_service.calculate_soil_health_score(acidic_soil)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            acidic_soil, score
        )
        
        # Check for pH-related recommendation
        ph_recs = [r for r in recommendations if r['parameter'] == 'pH Level']
        assert len(ph_recs) > 0, "Should have pH recommendation for acidic soil"
        assert 'lime' in ph_recs[0]['recommendation'].lower(), "Should recommend lime for acidic soil"
    
    def test_alkaline_soil_gets_sulfur_recommendation(self, soil_testing_service):
        """Test that alkaline soil gets sulfur/gypsum recommendation"""
        alkaline_soil = {
            'ph_level': 9.0,
            'nitrogen_kg_per_ha': 400
        }
        
        score = soil_testing_service.calculate_soil_health_score(alkaline_soil)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            alkaline_soil, score
        )
        
        # Check for pH-related recommendation
        ph_recs = [r for r in recommendations if r['parameter'] == 'pH Level']
        assert len(ph_recs) > 0, "Should have pH recommendation for alkaline soil"
        assert any(word in ph_recs[0]['recommendation'].lower() for word in ['sulfur', 'gypsum']), \
            "Should recommend sulfur or gypsum for alkaline soil"
    
    def test_low_nitrogen_gets_fertilizer_recommendation(self, soil_testing_service):
        """Test that low nitrogen gets urea recommendation"""
        low_n_soil = {
            'nitrogen_kg_per_ha': 150,
            'ph_level': 6.5
        }
        
        score = soil_testing_service.calculate_soil_health_score(low_n_soil)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            low_n_soil, score
        )
        
        # Check for nitrogen recommendation
        n_recs = [r for r in recommendations if r['parameter'] == 'Nitrogen']
        assert len(n_recs) > 0, "Should have nitrogen recommendation"
        assert 'urea' in n_recs[0]['recommendation'].lower(), "Should recommend urea for low nitrogen"
    
    def test_low_phosphorus_gets_dap_recommendation(self, soil_testing_service):
        """Test that low phosphorus gets DAP recommendation"""
        low_p_soil = {
            'phosphorus_kg_per_ha': 10,
            'ph_level': 6.5
        }
        
        score = soil_testing_service.calculate_soil_health_score(low_p_soil)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            low_p_soil, score
        )
        
        # Check for phosphorus recommendation
        p_recs = [r for r in recommendations if r['parameter'] == 'Phosphorus']
        assert len(p_recs) > 0, "Should have phosphorus recommendation"
        assert 'dap' in p_recs[0]['recommendation'].lower(), "Should recommend DAP for low phosphorus"
    
    def test_low_potassium_gets_mop_recommendation(self, soil_testing_service):
        """Test that low potassium gets MOP recommendation"""
        low_k_soil = {
            'potassium_kg_per_ha': 150,
            'ph_level': 6.5
        }
        
        score = soil_testing_service.calculate_soil_health_score(low_k_soil)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            low_k_soil, score
        )
        
        # Check for potassium recommendation
        k_recs = [r for r in recommendations if r['parameter'] == 'Potassium']
        assert len(k_recs) > 0, "Should have potassium recommendation"
        assert 'mop' in k_recs[0]['recommendation'].lower() or 'potash' in k_recs[0]['recommendation'].lower(), \
            "Should recommend MOP for low potassium"
    
    def test_low_organic_carbon_gets_manure_recommendation(self, soil_testing_service):
        """Test that low organic carbon gets organic matter recommendation"""
        low_oc_soil = {
            'organic_carbon_percent': 0.2,
            'ph_level': 6.5
        }
        
        score = soil_testing_service.calculate_soil_health_score(low_oc_soil)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            low_oc_soil, score
        )
        
        # Check for organic carbon recommendation
        oc_recs = [r for r in recommendations if r['parameter'] == 'Organic Carbon']
        assert len(oc_recs) > 0, "Should have organic carbon recommendation"
        assert any(word in oc_recs[0]['recommendation'].lower() for word in ['manure', 'compost']), \
            "Should recommend organic matter addition"
    
    def test_zinc_deficiency_gets_zinc_sulfate_recommendation(self, soil_testing_service):
        """Test that zinc deficiency gets zinc sulfate recommendation"""
        zn_deficient_soil = {
            'zinc_ppm': 0.3,
            'ph_level': 6.5
        }
        
        score = soil_testing_service.calculate_soil_health_score(zn_deficient_soil)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            zn_deficient_soil, score
        )
        
        # Check for zinc recommendation
        zn_recs = [r for r in recommendations if r['parameter'] == 'Zinc']
        assert len(zn_recs) > 0, "Should have zinc recommendation"
        assert 'zinc' in zn_recs[0]['recommendation'].lower(), "Should recommend zinc application"
    
    def test_high_salinity_gets_drainage_recommendation(self, soil_testing_service):
        """Test that high salinity gets drainage and gypsum recommendation"""
        saline_soil = {
            'electrical_conductivity': 3.0,
            'ph_level': 6.5
        }
        
        score = soil_testing_service.calculate_soil_health_score(saline_soil)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            saline_soil, score
        )
        
        # Check for EC recommendation
        ec_recs = [r for r in recommendations if r['parameter'] == 'Electrical Conductivity']
        assert len(ec_recs) > 0, "Should have salinity recommendation"
        assert 'drainage' in ec_recs[0]['recommendation'].lower() or 'gypsum' in ec_recs[0]['recommendation'].lower(), \
            "Should recommend drainage or gypsum for salinity"
    
    def test_poor_overall_health_gets_comprehensive_recommendation(self, soil_testing_service, poor_soil_data):
        """Test that poor overall health gets comprehensive improvement plan"""
        score = soil_testing_service.calculate_soil_health_score(poor_soil_data)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            poor_soil_data, score
        )
        
        # Should have overall health recommendation
        overall_recs = [r for r in recommendations if r['parameter'] == 'Overall Soil Health']
        assert len(overall_recs) > 0, "Should have overall health recommendation for poor soil"
        # Priority should be critical or medium depending on score
        assert overall_recs[0]['priority'] in ['critical', 'medium'], "Poor soil should have high priority"
    
    def test_optimal_soil_gets_fewer_recommendations(self, soil_testing_service, optimal_soil_data):
        """Test that optimal soil gets fewer recommendations"""
        score = soil_testing_service.calculate_soil_health_score(optimal_soil_data)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            optimal_soil_data, score
        )
        
        # Optimal soil should have few or no recommendations
        assert len(recommendations) <= 2, "Optimal soil should have minimal recommendations"
    
    def test_recommendations_have_required_fields(self, soil_testing_service, poor_soil_data):
        """Test that all recommendations have required fields"""
        score = soil_testing_service.calculate_soil_health_score(poor_soil_data)
        recommendations = soil_testing_service.generate_soil_improvement_recommendations(
            poor_soil_data, score
        )
        
        required_fields = ['priority', 'parameter', 'current_value', 'issue', 'recommendation', 'expected_improvement', 'timeline']
        
        for rec in recommendations:
            for field in required_fields:
                assert field in rec, f"Recommendation missing required field: {field}"


class TestManualDataParsing:
    """Test manual soil test data parsing"""
    
    def test_parse_complete_manual_entry(self, soil_testing_service):
        """Test parsing complete manual entry"""
        manual_data = {
            'nitrogen_kg_per_ha': 400.0,
            'phosphorus_kg_per_ha': 35.0,
            'potassium_kg_per_ha': 350.0,
            'ph_level': 6.5,
            'organic_carbon_percent': 0.6,
            'zinc_ppm': 0.8,
            'lab_name': 'ICAR Soil Testing Lab',
            'lab_reference_number': 'STL-2024-001'
        }
        
        parsed = soil_testing_service.parse_soil_test_manual_entry(manual_data)
        
        assert parsed['nitrogen_kg_per_ha'] == 400.0
        assert parsed['phosphorus_kg_per_ha'] == 35.0
        assert parsed['potassium_kg_per_ha'] == 350.0
        assert parsed['ph_level'] == 6.5
        assert parsed['lab_name'] == 'ICAR Soil Testing Lab'
    
    def test_parse_partial_manual_entry(self, soil_testing_service):
        """Test parsing partial manual entry"""
        partial_data = {
            'ph_level': 6.5,
            'nitrogen_kg_per_ha': 400.0
        }
        
        parsed = soil_testing_service.parse_soil_test_manual_entry(partial_data)
        
        assert parsed['ph_level'] == 6.5
        assert parsed['nitrogen_kg_per_ha'] == 400.0
        assert len(parsed) == 2
    
    def test_parse_rejects_invalid_ph(self, soil_testing_service):
        """Test that invalid pH values are rejected"""
        invalid_data = {
            'ph_level': 15.0  # Invalid: pH must be 0-14
        }
        
        with pytest.raises(ValueError, match="pH level must be between 0 and 14"):
            soil_testing_service.parse_soil_test_manual_entry(invalid_data)
    
    def test_parse_handles_none_values(self, soil_testing_service):
        """Test that None values are handled correctly"""
        data_with_none = {
            'ph_level': 6.5,
            'nitrogen_kg_per_ha': None,
            'phosphorus_kg_per_ha': 35.0
        }
        
        parsed = soil_testing_service.parse_soil_test_manual_entry(data_with_none)
        
        assert parsed['ph_level'] == 6.5
        assert parsed['phosphorus_kg_per_ha'] == 35.0
        assert 'nitrogen_kg_per_ha' not in parsed


class TestSoilTestComparison:
    """Test soil test comparison functionality"""
    
    def test_compare_shows_improvements(self, soil_testing_service, poor_soil_data, optimal_soil_data):
        """Test that comparison shows improvements"""
        # Add soil health scores
        poor_soil_data['soil_health_score'] = soil_testing_service.calculate_soil_health_score(poor_soil_data)
        optimal_soil_data['soil_health_score'] = soil_testing_service.calculate_soil_health_score(optimal_soil_data)
        
        changes = soil_testing_service.compare_soil_tests(poor_soil_data, optimal_soil_data)
        
        # Should show improvements in multiple parameters
        assert 'soil_health_score' in changes
        assert changes['soil_health_score']['trend'] == 'improving'
        assert changes['soil_health_score']['change'] > 0
    
    def test_compare_shows_declines(self, soil_testing_service, optimal_soil_data, poor_soil_data):
        """Test that comparison shows declines"""
        # Add soil health scores
        optimal_soil_data['soil_health_score'] = soil_testing_service.calculate_soil_health_score(optimal_soil_data)
        poor_soil_data['soil_health_score'] = soil_testing_service.calculate_soil_health_score(poor_soil_data)
        
        changes = soil_testing_service.compare_soil_tests(optimal_soil_data, poor_soil_data)
        
        # Should show declines
        assert 'soil_health_score' in changes
        assert changes['soil_health_score']['trend'] == 'declining'
        assert changes['soil_health_score']['change'] < 0
    
    def test_compare_shows_stable_values(self, soil_testing_service, optimal_soil_data):
        """Test that comparison shows stable values"""
        # Compare same data
        optimal_soil_data['soil_health_score'] = soil_testing_service.calculate_soil_health_score(optimal_soil_data)
        
        changes = soil_testing_service.compare_soil_tests(optimal_soil_data, optimal_soil_data)
        
        # All parameters should be stable
        for param, change_data in changes.items():
            assert change_data['trend'] == 'stable'
            assert change_data['change'] == 0
    
    def test_compare_calculates_percent_change(self, soil_testing_service):
        """Test that comparison calculates percent change correctly"""
        test1 = {'nitrogen_kg_per_ha': 200.0}
        test2 = {'nitrogen_kg_per_ha': 300.0}
        
        changes = soil_testing_service.compare_soil_tests(test1, test2)
        
        assert 'nitrogen_kg_per_ha' in changes
        assert changes['nitrogen_kg_per_ha']['percent_change'] == 50.0  # 50% increase
    
    def test_compare_handles_missing_parameters(self, soil_testing_service):
        """Test that comparison handles missing parameters gracefully"""
        test1 = {'ph_level': 6.5, 'nitrogen_kg_per_ha': 400.0}
        test2 = {'ph_level': 6.8}  # Missing nitrogen
        
        changes = soil_testing_service.compare_soil_tests(test1, test2)
        
        # Should only compare pH (common parameter)
        assert 'ph_level' in changes
        assert 'nitrogen_kg_per_ha' not in changes


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
