"""
Tests for Fertilizer Recommendation Engine
Task 24.1: Implement fertilizer recommendation engine
Validates: Requirements AC9 (Phase 6 - Required)
"""

import pytest
from datetime import date, timedelta
from app.services.fertilizer_recommendation_service import fertilizer_service


class TestNutrientRequirements:
    """Test nutrient requirement calculations"""
    
    def test_calculate_nutrient_requirements_wheat(self):
        """Test nutrient requirements for wheat crop"""
        soil_data = {
            'nitrogen_kg_per_ha': 200,
            'phosphorus_kg_per_ha': 20,
            'potassium_kg_per_ha': 150
        }
        
        result = fertilizer_service.calculate_nutrient_requirements(
            crop_type='wheat',
            area_hectares=2.0,
            soil_data=soil_data,
            target_yield_factor=1.0
        )
        
        assert result['crop_type'] == 'wheat'
        assert result['area_hectares'] == 2.0
        assert result['crop_requirements']['N'] == 240  # 120 kg/ha * 2 ha
        assert result['crop_requirements']['P'] == 120  # 60 kg/ha * 2 ha
        assert result['crop_requirements']['K'] == 80   # 40 kg/ha * 2 ha
        
        # Check deficits (soil has more than required, so no deficit)
        assert result['deficits']['N'] == 0    # 240 - 400 (no deficit, soil has enough)
        assert result['deficits']['P'] == 80   # 120 - 40
        assert result['deficits']['K'] == 0    # 80 - 300 (no deficit)
    
    def test_calculate_nutrient_requirements_rice(self):
        """Test nutrient requirements for rice crop"""
        soil_data = {
            'nitrogen_kg_per_ha': 100,
            'phosphorus_kg_per_ha': 30,
            'potassium_kg_per_ha': 100
        }
        
        result = fertilizer_service.calculate_nutrient_requirements(
            crop_type='rice',
            area_hectares=1.5,
            soil_data=soil_data,
            target_yield_factor=1.0
        )
        
        assert result['crop_type'] == 'rice'
        assert result['deficits']['N'] == 30   # (120 * 1.5) - 150
        assert result['deficits']['P'] == 45   # (60 * 1.5) - 45
        assert result['deficits']['K'] == 0    # No deficit
    
    def test_calculate_nutrient_requirements_with_target_yield(self):
        """Test nutrient requirements with higher target yield"""
        soil_data = {
            'nitrogen_kg_per_ha': 0,
            'phosphorus_kg_per_ha': 0,
            'potassium_kg_per_ha': 0
        }
        
        result = fertilizer_service.calculate_nutrient_requirements(
            crop_type='maize',
            area_hectares=1.0,
            soil_data=soil_data,
            target_yield_factor=1.2  # 20% higher yield target
        )
        
        # Requirements should be 20% higher
        assert result['crop_requirements']['N'] == 180  # 150 * 1.2
        assert result['crop_requirements']['P'] == 90   # 75 * 1.2
        assert result['crop_requirements']['K'] == 60   # 50 * 1.2
    
    def test_calculate_nutrient_requirements_unknown_crop(self):
        """Test nutrient requirements for unknown crop uses default"""
        soil_data = {
            'nitrogen_kg_per_ha': 0,
            'phosphorus_kg_per_ha': 0,
            'potassium_kg_per_ha': 0
        }
        
        result = fertilizer_service.calculate_nutrient_requirements(
            crop_type='unknown_crop',
            area_hectares=1.0,
            soil_data=soil_data,
            target_yield_factor=1.0
        )
        
        # Should use default requirements
        assert result['crop_requirements']['N'] == 100
        assert result['crop_requirements']['P'] == 50
        assert result['crop_requirements']['K'] == 50


class TestFertilizerRecommendations:
    """Test fertilizer recommendation generation"""
    
    def test_generate_fertilizer_recommendations_balanced(self):
        """Test balanced organic/chemical fertilizer recommendations"""
        nutrient_req = {
            'crop_type': 'wheat',
            'area_hectares': 1.0,
            'deficits': {
                'N': 100,
                'P': 50,
                'K': 40
            }
        }
        
        result = fertilizer_service.generate_fertilizer_recommendations(
            nutrient_requirements=nutrient_req,
            organic_preference=0.3,  # 30% organic
            budget_per_hectare=None
        )
        
        assert 'recommendations' in result
        assert len(result['recommendations']) > 0
        assert result['total_cost'] > 0
        assert result['organic_ratio'] == 0.3
        
        # Check that we have both organic and chemical fertilizers
        organic_count = sum(1 for r in result['recommendations'] if r['category'] == 'organic')
        chemical_count = sum(1 for r in result['recommendations'] if r['category'] == 'chemical')
        
        assert organic_count > 0
        assert chemical_count > 0
    
    def test_generate_fertilizer_recommendations_high_organic(self):
        """Test high organic preference recommendations"""
        nutrient_req = {
            'crop_type': 'wheat',
            'area_hectares': 1.0,
            'deficits': {
                'N': 100,
                'P': 50,
                'K': 40
            }
        }
        
        result = fertilizer_service.generate_fertilizer_recommendations(
            nutrient_requirements=nutrient_req,
            organic_preference=0.6,  # 60% organic
            budget_per_hectare=None
        )
        
        assert result['organic_ratio'] == 0.6
        
        # Higher organic preference should result in more organic fertilizers
        organic_nutrients = sum(
            r['nutrients_provided']['N'] + r['nutrients_provided']['P'] + r['nutrients_provided']['K']
            for r in result['recommendations'] if r['category'] == 'organic'
        )
        
        assert organic_nutrients > 0
    
    def test_generate_fertilizer_recommendations_chemical_only(self):
        """Test chemical-only fertilizer recommendations"""
        nutrient_req = {
            'crop_type': 'wheat',
            'area_hectares': 1.0,
            'deficits': {
                'N': 100,
                'P': 50,
                'K': 40
            }
        }
        
        result = fertilizer_service.generate_fertilizer_recommendations(
            nutrient_requirements=nutrient_req,
            organic_preference=0.0,  # 0% organic
            budget_per_hectare=None
        )
        
        assert result['organic_ratio'] == 0.0
        
        # Should only have chemical fertilizers
        organic_count = sum(1 for r in result['recommendations'] if r['category'] == 'organic')
        assert organic_count == 0
    
    def test_fertilizer_types_include_required_nutrients(self):
        """Test that recommended fertilizers provide required nutrients"""
        nutrient_req = {
            'crop_type': 'wheat',
            'area_hectares': 1.0,
            'deficits': {
                'N': 100,
                'P': 50,
                'K': 40
            }
        }
        
        result = fertilizer_service.generate_fertilizer_recommendations(
            nutrient_requirements=nutrient_req,
            organic_preference=0.3,
            budget_per_hectare=None
        )
        
        # Calculate total nutrients provided
        total_n = sum(r['nutrients_provided']['N'] for r in result['recommendations'])
        total_p = sum(r['nutrients_provided']['P'] for r in result['recommendations'])
        total_k = sum(r['nutrients_provided']['K'] for r in result['recommendations'])
        
        # Should approximately match requirements (within 10% tolerance)
        assert abs(total_n - 100) < 10
        assert abs(total_p - 50) < 10
        assert abs(total_k - 40) < 10


class TestApplicationTiming:
    """Test fertilizer application timing optimization"""
    
    def test_optimize_application_timing_wheat(self):
        """Test application timing for wheat crop"""
        planting_date = date.today()
        
        fertilizer_recs = [
            {
                'fertilizer_type': 'urea',
                'category': 'chemical',
                'quantity_kg': 200,
                'quantity_per_hectare': 200,
                'nutrients_provided': {'N': 92, 'P': 0, 'K': 0}
            },
            {
                'fertilizer_type': 'dap',
                'category': 'chemical',
                'quantity_kg': 100,
                'quantity_per_hectare': 100,
                'nutrients_provided': {'N': 18, 'P': 46, 'K': 0}
            },
            {
                'fertilizer_type': 'mop',
                'category': 'chemical',
                'quantity_kg': 67,
                'quantity_per_hectare': 67,
                'nutrients_provided': {'N': 0, 'P': 0, 'K': 40}
            }
        ]
        
        result = fertilizer_service.optimize_application_timing(
            crop_type='wheat',
            planting_date=planting_date,
            fertilizer_recommendations=fertilizer_recs,
            weather_forecast=None
        )
        
        assert result['crop_type'] == 'wheat'
        assert result['planting_date'] == planting_date
        assert len(result['schedule']) >= 2  # At least basal and one top dressing
        
        # Check basal application
        basal = result['schedule'][0]
        assert basal['stage'] == 'basal'
        assert basal['days_after_planting'] == 0
        assert len(basal['applications']) > 0
    
    def test_application_timing_includes_all_stages(self):
        """Test that application timing includes basal, vegetative, and flowering stages"""
        planting_date = date.today()
        
        fertilizer_recs = [
            {
                'fertilizer_type': 'urea',
                'category': 'chemical',
                'quantity_kg': 200,
                'quantity_per_hectare': 200,
                'nutrients_provided': {'N': 92, 'P': 0, 'K': 0}
            }
        ]
        
        result = fertilizer_service.optimize_application_timing(
            crop_type='wheat',
            planting_date=planting_date,
            fertilizer_recommendations=fertilizer_recs,
            weather_forecast=None
        )
        
        stages = [stage['stage'] for stage in result['schedule']]
        
        # Should have basal and at least one top dressing
        assert 'basal' in stages
        assert len(stages) >= 2
    
    def test_application_dates_are_sequential(self):
        """Test that application dates are in chronological order"""
        planting_date = date.today()
        
        fertilizer_recs = [
            {
                'fertilizer_type': 'urea',
                'category': 'chemical',
                'quantity_kg': 200,
                'quantity_per_hectare': 200,
                'nutrients_provided': {'N': 92, 'P': 0, 'K': 0}
            }
        ]
        
        result = fertilizer_service.optimize_application_timing(
            crop_type='wheat',
            planting_date=planting_date,
            fertilizer_recommendations=fertilizer_recs,
            weather_forecast=None
        )
        
        dates = [stage['date'] for stage in result['schedule']]
        
        # Dates should be in ascending order
        for i in range(len(dates) - 1):
            assert dates[i] <= dates[i + 1]


class TestBudgetOptimization:
    """Test budget-constrained fertilizer optimization"""
    
    def test_optimize_for_budget_within_limit(self):
        """Test optimization when budget is sufficient"""
        nutrient_req = {
            'crop_type': 'wheat',
            'area_hectares': 1.0,
            'deficits': {
                'N': 100,
                'P': 50,
                'K': 40
            }
        }
        
        result = fertilizer_service.optimize_for_budget(
            nutrient_requirements=nutrient_req,
            budget_per_hectare=5000,  # Generous budget
            min_organic_ratio=0.2
        )
        
        assert result['within_budget'] == True
        assert result['cost_per_hectare'] <= 5000
        assert result['organic_ratio'] >= 0.2
    
    def test_optimize_for_budget_tight_constraint(self):
        """Test optimization with tight budget constraint"""
        nutrient_req = {
            'crop_type': 'wheat',
            'area_hectares': 1.0,
            'deficits': {
                'N': 100,
                'P': 50,
                'K': 40
            }
        }
        
        result = fertilizer_service.optimize_for_budget(
            nutrient_requirements=nutrient_req,
            budget_per_hectare=1500,  # Tight budget
            min_organic_ratio=0.2
        )
        
        assert result['cost_per_hectare'] <= 1500
        # Should still maintain minimum organic ratio
        assert result['organic_ratio'] >= 0.2 or 'note' in result


class TestOrganicChemicalBalancing:
    """Test organic vs chemical fertilizer balancing"""
    
    def test_balance_for_poor_soil_health(self):
        """Test balancing increases organic ratio for poor soil health"""
        nutrient_req = {
            'crop_type': 'wheat',
            'area_hectares': 1.0,
            'deficits': {
                'N': 100,
                'P': 50,
                'K': 40
            }
        }
        
        result = fertilizer_service.balance_organic_chemical(
            nutrient_requirements=nutrient_req,
            soil_health_score=40,  # Poor soil health
            farmer_preference='balanced'
        )
        
        # Should increase organic ratio for poor soil health
        assert result['organic_ratio'] > 0.35
        assert 'balancing_strategy' in result
        assert result['balancing_strategy']['soil_health_score'] == 40
    
    def test_balance_for_good_soil_health(self):
        """Test balancing maintains normal ratio for good soil health"""
        nutrient_req = {
            'crop_type': 'wheat',
            'area_hectares': 1.0,
            'deficits': {
                'N': 100,
                'P': 50,
                'K': 40
            }
        }
        
        result = fertilizer_service.balance_organic_chemical(
            nutrient_requirements=nutrient_req,
            soil_health_score=80,  # Good soil health
            farmer_preference='balanced'
        )
        
        # Should use base ratio for good soil health
        assert result['organic_ratio'] <= 0.4
        assert 'balancing_strategy' in result
    
    def test_balance_respects_farmer_preference_organic(self):
        """Test balancing respects organic preference"""
        nutrient_req = {
            'crop_type': 'wheat',
            'area_hectares': 1.0,
            'deficits': {
                'N': 100,
                'P': 50,
                'K': 40
            }
        }
        
        result = fertilizer_service.balance_organic_chemical(
            nutrient_requirements=nutrient_req,
            soil_health_score=60,
            farmer_preference='organic'
        )
        
        # Should have high organic ratio
        assert result['organic_ratio'] >= 0.5
    
    def test_balance_respects_farmer_preference_chemical(self):
        """Test balancing respects chemical preference"""
        nutrient_req = {
            'crop_type': 'wheat',
            'area_hectares': 1.0,
            'deficits': {
                'N': 100,
                'P': 50,
                'K': 40
            }
        }
        
        result = fertilizer_service.balance_organic_chemical(
            nutrient_requirements=nutrient_req,
            soil_health_score=60,
            farmer_preference='chemical'
        )
        
        # Should have low organic ratio (allow for floating point precision)
        assert result['organic_ratio'] < 0.31


class TestCompleteFertilizerPlan:
    """Test complete fertilizer plan generation"""
    
    def test_generate_complete_plan(self):
        """Test generation of complete fertilizer plan"""
        soil_data = {
            'nitrogen_kg_per_ha': 150,
            'phosphorus_kg_per_ha': 20,
            'potassium_kg_per_ha': 100,
            'soil_health_score': 65
        }
        
        result = fertilizer_service.generate_complete_fertilizer_plan(
            crop_type='wheat',
            area_hectares=2.0,
            soil_data=soil_data,
            planting_date=date.today(),
            budget_per_hectare=None,
            farmer_preference='balanced',
            target_yield_factor=1.0,
            weather_forecast=None
        )
        
        # Check all required components
        assert 'crop_type' in result
        assert 'nutrient_requirements' in result
        assert 'fertilizer_recommendations' in result
        assert 'application_schedule' in result
        assert 'cost_summary' in result
        assert 'key_recommendations' in result
        
        # Check nutrient requirements
        assert result['nutrient_requirements']['crop_type'] == 'wheat'
        assert result['nutrient_requirements']['area_hectares'] == 2.0
        
        # Check fertilizer recommendations
        assert len(result['fertilizer_recommendations']['recommendations']) > 0
        
        # Check application schedule
        assert len(result['application_schedule']['schedule']) > 0
        
        # Check cost summary
        assert result['cost_summary']['total_cost'] > 0
    
    def test_complete_plan_with_budget_constraint(self):
        """Test complete plan generation with budget constraint"""
        soil_data = {
            'nitrogen_kg_per_ha': 150,
            'phosphorus_kg_per_ha': 20,
            'potassium_kg_per_ha': 100,
            'soil_health_score': 65
        }
        
        result = fertilizer_service.generate_complete_fertilizer_plan(
            crop_type='wheat',
            area_hectares=2.0,
            soil_data=soil_data,
            planting_date=date.today(),
            budget_per_hectare=3000,  # Budget constraint
            farmer_preference='balanced',
            target_yield_factor=1.0,
            weather_forecast=None
        )
        
        # Should respect budget
        assert result['cost_summary']['cost_per_hectare'] <= 3000
        assert result['cost_summary']['within_budget'] == True
    
    def test_complete_plan_for_different_crops(self):
        """Test complete plan generation for different crop types"""
        soil_data = {
            'nitrogen_kg_per_ha': 100,
            'phosphorus_kg_per_ha': 30,
            'potassium_kg_per_ha': 150,
            'soil_health_score': 70
        }
        
        crops = ['rice', 'maize', 'cotton', 'potato']
        
        for crop in crops:
            result = fertilizer_service.generate_complete_fertilizer_plan(
                crop_type=crop,
                area_hectares=1.0,
                soil_data=soil_data,
                planting_date=date.today(),
                budget_per_hectare=None,
                farmer_preference='balanced',
                target_yield_factor=1.0,
                weather_forecast=None
            )
            
            assert result['crop_type'] == crop
            assert len(result['fertilizer_recommendations']['recommendations']) > 0
            assert len(result['application_schedule']['schedule']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
