"""
Tests for Livestock Nutrition Advisor
Task 28.1: Implement AI-powered nutrition advisor

Tests cover:
- Personalized feeding recommendations
- Feed cost optimization
- Growth stage nutritional planning
- Feed efficiency reports
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, date

from app.services.livestock_nutrition_service import LivestockNutritionService, nutrition_service


class TestFeedingRecommendations:
    """Test personalized feeding recommendations"""
    
    def test_get_feeding_recommendations_cattle_dairy(self):
        """Test feeding recommendations for dairy cattle"""
        service = LivestockNutritionService()
        
        # Mock Bedrock response
        mock_response = {
            "daily_requirements": {
                "dry_matter_intake_kg": 15.0,
                "crude_protein_grams": 1800,
                "tdn_kg": 10.5,
                "metabolizable_energy_mj": 180.0,
                "calcium_grams": 80,
                "phosphorus_grams": 50,
                "vitamins_minerals": ["Vitamin A", "Vitamin D", "Vitamin E"]
            },
            "feed_composition": {
                "green_fodder_kg": 25.0,
                "dry_fodder_kg": 6.0,
                "concentrate_kg": 4.0,
                "mineral_mixture_grams": 50,
                "salt_grams": 30,
                "water_liters": 50
            },
            "feed_ingredients": [
                {
                    "ingredient": "Green Maize Fodder",
                    "quantity_kg": 25.0,
                    "quality_requirement": "Fresh, leafy",
                    "locally_available": True
                }
            ],
            "feeding_schedule": {
                "meals_per_day": 3,
                "schedule": [
                    {
                        "time": "6:00 AM",
                        "feed_type": "Green fodder",
                        "quantity": "10 kg"
                    }
                ]
            },
            "special_considerations": [
                "Ensure clean water availability",
                "Monitor milk production"
            ],
            "cost_estimation": {
                "daily_cost_inr": 180,
                "monthly_cost_inr": 5400,
                "cost_breakdown": {
                    "green_fodder": 50,
                    "dry_fodder": 30,
                    "concentrate": 80,
                    "mineral_mixture": 20
                }
            },
            "growth_stage": "adult",
            "confidence_score": 0.85
        }
        
        with patch.object(service.bedrock, '_invoke_claude', return_value=json.dumps(mock_response)):
            recommendations = service.get_feeding_recommendations(
                species="cattle",
                breed="Holstein Friesian",
                age_months=36,
                weight_kg=450.0,
                purpose="dairy",
                lactation_status="peak_lactation",
                milk_production_liters=15.0,
                location_state="Punjab"
            )
            
            # Verify structure
            assert "daily_requirements" in recommendations
            assert "feed_composition" in recommendations
            assert "feeding_schedule" in recommendations
            assert "cost_estimation" in recommendations
            
            # Verify daily requirements
            assert recommendations["daily_requirements"]["dry_matter_intake_kg"] > 0
            assert recommendations["daily_requirements"]["crude_protein_grams"] > 0
            
            # Verify feed composition
            assert recommendations["feed_composition"]["green_fodder_kg"] > 0
            assert recommendations["feed_composition"]["concentrate_kg"] > 0
            
            # Verify cost estimation
            assert recommendations["cost_estimation"]["daily_cost_inr"] > 0
            assert recommendations["cost_estimation"]["monthly_cost_inr"] > 0
    
    def test_get_feeding_recommendations_goat_meat(self):
        """Test feeding recommendations for meat goat"""
        service = LivestockNutritionService()
        
        mock_response = {
            "daily_requirements": {
                "dry_matter_intake_kg": 1.5,
                "crude_protein_grams": 180,
                "tdn_kg": 1.0,
                "metabolizable_energy_mj": 18.0,
                "calcium_grams": 8,
                "phosphorus_grams": 5,
                "vitamins_minerals": ["Vitamin A", "Vitamin D"]
            },
            "feed_composition": {
                "green_fodder_kg": 3.0,
                "dry_fodder_kg": 0.5,
                "concentrate_kg": 0.3,
                "mineral_mixture_grams": 10,
                "salt_grams": 5,
                "water_liters": 5
            },
            "feed_ingredients": [],
            "feeding_schedule": {
                "meals_per_day": 2,
                "schedule": []
            },
            "special_considerations": ["Provide clean water", "Monitor weight gain"],
            "cost_estimation": {
                "daily_cost_inr": 25,
                "monthly_cost_inr": 750,
                "cost_breakdown": {}
            },
            "growth_stage": "growing",
            "confidence_score": 0.80
        }
        
        import json
        with patch.object(service.bedrock, '_invoke_claude', return_value=json.dumps(mock_response)):
            recommendations = service.get_feeding_recommendations(
                species="goat",
                breed="Boer",
                age_months=8,
                weight_kg=25.0,
                purpose="meat"
            )
            
            assert recommendations["daily_requirements"]["dry_matter_intake_kg"] > 0
            assert recommendations["cost_estimation"]["daily_cost_inr"] > 0
    
    def test_determine_growth_stage_cattle(self):
        """Test growth stage determination for cattle"""
        service = LivestockNutritionService()
        
        # Test calf stage
        stage = service._determine_growth_stage("cattle", 3, None)
        assert stage == "calf"
        
        # Test growing stage
        stage = service._determine_growth_stage("cattle", 12, None)
        assert stage == "growing"
        
        # Test adult stage
        stage = service._determine_growth_stage("cattle", 24, None)
        assert stage == "adult"
        
        # Test lactating stage
        stage = service._determine_growth_stage("cattle", 36, "peak_lactation")
        assert stage == "lactating_peak_lactation"
    
    def test_fallback_recommendations(self):
        """Test fallback recommendations when Bedrock fails"""
        service = LivestockNutritionService()
        
        fallback = service._create_fallback_recommendations("cattle", 400.0, "dairy")
        
        assert "daily_requirements" in fallback
        assert "feed_composition" in fallback
        assert "cost_estimation" in fallback
        assert fallback["confidence_score"] == 0.5


class TestFeedCostOptimization:
    """Test feed cost optimization engine"""
    
    def test_optimize_feed_cost_basic(self):
        """Test basic feed cost optimization"""
        service = LivestockNutritionService()
        
        nutritional_requirements = {
            "dry_matter_intake_kg": 15.0,
            "crude_protein_grams": 1800,
            "tdn_kg": 10.5
        }
        
        available_feeds = [
            {
                "name": "Green Maize Fodder",
                "price_per_kg": 2.0,
                "protein_percentage": 2.5,
                "energy_mj_per_kg": 2.8,
                "locally_available": True
            },
            {
                "name": "Cotton Seed Cake",
                "price_per_kg": 25.0,
                "protein_percentage": 22.0,
                "energy_mj_per_kg": 11.0,
                "locally_available": True
            }
        ]
        
        mock_response = {
            "optimized_plan": {
                "ingredients": [
                    {
                        "name": "Green Maize Fodder",
                        "quantity_kg": 20.0,
                        "cost_inr": 40,
                        "nutritional_contribution": {
                            "protein_grams": 500,
                            "energy_mj": 56.0
                        }
                    },
                    {
                        "name": "Cotton Seed Cake",
                        "quantity_kg": 2.0,
                        "cost_inr": 50,
                        "nutritional_contribution": {
                            "protein_grams": 440,
                            "energy_mj": 22.0
                        }
                    }
                ],
                "total_daily_cost_inr": 90,
                "total_monthly_cost_inr": 2700,
                "cost_per_kg_feed": 4.09
            },
            "nutritional_adequacy": {
                "protein_met": True,
                "energy_met": True,
                "minerals_met": True,
                "adequacy_percentage": 100
            },
            "alternative_options": [],
            "cost_savings": {
                "vs_standard_feeding": 30,
                "percentage_saved": 10.0
            },
            "confidence_score": 0.85
        }
        
        with patch.object(service.bedrock, '_invoke_claude', return_value=json.dumps(mock_response)):
            optimization = service.optimize_feed_cost(
                species="cattle",
                weight_kg=450.0,
                purpose="dairy",
                nutritional_requirements=nutritional_requirements,
                available_feeds=available_feeds,
                location_state="Punjab"
            )
            
            assert "optimized_plan" in optimization
            assert "nutritional_adequacy" in optimization
            assert optimization["optimized_plan"]["total_daily_cost_inr"] > 0
            assert optimization["nutritional_adequacy"]["protein_met"] is True
    
    def test_optimize_feed_cost_with_alternatives(self):
        """Test feed optimization with alternative options"""
        service = LivestockNutritionService()
        
        nutritional_requirements = {
            "dry_matter_intake_kg": 10.0,
            "crude_protein_grams": 1200
        }
        
        available_feeds = [
            {"name": "Feed A", "price_per_kg": 10.0, "protein_percentage": 15.0, "energy_mj_per_kg": 10.0, "locally_available": True},
            {"name": "Feed B", "price_per_kg": 15.0, "protein_percentage": 20.0, "energy_mj_per_kg": 12.0, "locally_available": True},
            {"name": "Feed C", "price_per_kg": 8.0, "protein_percentage": 12.0, "energy_mj_per_kg": 9.0, "locally_available": True}
        ]
        
        mock_response = {
            "optimized_plan": {
                "ingredients": [],
                "total_daily_cost_inr": 100,
                "total_monthly_cost_inr": 3000,
                "cost_per_kg_feed": 10.0
            },
            "nutritional_adequacy": {
                "protein_met": True,
                "energy_met": True,
                "minerals_met": True,
                "adequacy_percentage": 100
            },
            "alternative_options": [
                {
                    "option_name": "Alternative 1",
                    "daily_cost_inr": 110,
                    "cost_difference_inr": 10,
                    "trade_offs": "Higher protein content"
                },
                {
                    "option_name": "Alternative 2",
                    "daily_cost_inr": 95,
                    "cost_difference_inr": -5,
                    "trade_offs": "Lower quality ingredients"
                }
            ],
            "cost_savings": {
                "vs_standard_feeding": 20,
                "percentage_saved": 16.7
            },
            "confidence_score": 0.85
        }
        
        with patch.object(service.bedrock, '_invoke_claude', return_value=json.dumps(mock_response)):
            optimization = service.optimize_feed_cost(
                species="cattle",
                weight_kg=400.0,
                purpose="dairy",
                nutritional_requirements=nutritional_requirements,
                available_feeds=available_feeds
            )
            
            assert len(optimization["alternative_options"]) > 0
            assert "cost_savings" in optimization


class TestGrowthStageNutritionPlan:
    """Test growth stage nutritional planning"""
    
    def test_growth_stage_plan_cattle(self):
        """Test growth stage plan for cattle"""
        service = LivestockNutritionService()
        
        mock_response = {
            "current_stage": "growing",
            "stages": [
                {
                    "stage_name": "Calf",
                    "age_range_months": "0-6",
                    "nutritional_requirements": {
                        "protein_grams_per_day": 500,
                        "energy_mj_per_day": 30.0,
                        "calcium_grams": 20,
                        "phosphorus_grams": 15
                    },
                    "feed_composition": {
                        "milk_liters": 4.0,
                        "starter_feed_kg": 0.5,
                        "green_fodder_kg": 2.0,
                        "concentrate_kg": 0.3
                    },
                    "expected_growth_rate_kg_per_month": 15.0,
                    "monthly_cost_inr": 2000,
                    "special_care": ["Colostrum feeding", "Deworming"]
                },
                {
                    "stage_name": "Growing",
                    "age_range_months": "6-18",
                    "nutritional_requirements": {
                        "protein_grams_per_day": 1200,
                        "energy_mj_per_day": 100.0,
                        "calcium_grams": 50,
                        "phosphorus_grams": 30
                    },
                    "feed_composition": {
                        "milk_liters": 0.0,
                        "starter_feed_kg": 0.0,
                        "green_fodder_kg": 15.0,
                        "concentrate_kg": 2.0
                    },
                    "expected_growth_rate_kg_per_month": 25.0,
                    "monthly_cost_inr": 3500,
                    "special_care": ["Regular deworming", "Vaccination"]
                }
            ],
            "transition_guidelines": [
                {
                    "from_stage": "Calf",
                    "to_stage": "Growing",
                    "transition_period_days": 14,
                    "guidelines": ["Gradually reduce milk", "Increase concentrate"]
                }
            ],
            "total_cost_to_maturity": 50000,
            "expected_time_to_target_weight_months": 18,
            "confidence_score": 0.85
        }
        
        with patch.object(service.bedrock, '_invoke_claude', return_value=json.dumps(mock_response)):
            plan = service.get_growth_stage_nutrition_plan(
                species="cattle",
                breed="Holstein Friesian",
                purpose="dairy",
                current_age_months=12,
                current_weight_kg=200.0,
                target_weight_kg=450.0
            )
            
            assert "current_stage" in plan
            assert "stages" in plan
            assert len(plan["stages"]) > 0
            assert "transition_guidelines" in plan
            assert plan["total_cost_to_maturity"] > 0
    
    def test_growth_stage_plan_goat(self):
        """Test growth stage plan for goat"""
        service = LivestockNutritionService()
        
        mock_response = {
            "current_stage": "kid",
            "stages": [
                {
                    "stage_name": "Kid",
                    "age_range_months": "0-4",
                    "nutritional_requirements": {
                        "protein_grams_per_day": 80,
                        "energy_mj_per_day": 8.0,
                        "calcium_grams": 5,
                        "phosphorus_grams": 3
                    },
                    "feed_composition": {
                        "milk_liters": 1.0,
                        "starter_feed_kg": 0.1,
                        "green_fodder_kg": 0.5,
                        "concentrate_kg": 0.05
                    },
                    "expected_growth_rate_kg_per_month": 2.0,
                    "monthly_cost_inr": 500,
                    "special_care": ["Colostrum feeding", "Shelter"]
                }
            ],
            "transition_guidelines": [],
            "total_cost_to_maturity": 8000,
            "expected_time_to_target_weight_months": 12,
            "confidence_score": 0.80
        }
        
        with patch.object(service.bedrock, '_invoke_claude', return_value=json.dumps(mock_response)):
            plan = service.get_growth_stage_nutrition_plan(
                species="goat",
                breed="Boer",
                purpose="meat",
                current_age_months=2,
                current_weight_kg=8.0,
                target_weight_kg=35.0
            )
            
            assert plan["current_stage"] == "kid"
            assert len(plan["stages"]) > 0


class TestFeedEfficiencyReport:
    """Test feed efficiency reporting"""
    
    def test_generate_feed_efficiency_report_good_performance(self):
        """Test feed efficiency report for good performance"""
        service = LivestockNutritionService()
        
        mock_response = {
            "efficiency_metrics": {
                "weight_gain_kg": 50.0,
                "avg_daily_gain_kg": 0.556,
                "cost_per_kg_gain_inr": 180.0,
                "feed_conversion_ratio": 6.5,
                "efficiency_rating": "Good"
            },
            "benchmarks": {
                "industry_avg_daily_gain_kg": 0.500,
                "industry_avg_cost_per_kg_inr": 200.0,
                "performance_percentile": 70
            },
            "cost_analysis": {
                "total_feed_cost_inr": 9000.0,
                "cost_efficiency_rating": "Good",
                "potential_savings_inr": 500,
                "potential_savings_percentage": 5.6
            },
            "recommendations": [
                {
                    "category": "Feed Composition",
                    "recommendation": "Increase protein content slightly",
                    "expected_impact": "Improve daily gain by 10%",
                    "priority": "Medium"
                }
            ],
            "projected_improvements": {
                "improved_daily_gain_kg": 0.611,
                "improved_cost_per_kg_inr": 170.0,
                "timeline_days": 30,
                "expected_savings_monthly_inr": 500
            },
            "confidence_score": 0.85
        }
        
        with patch.object(service.bedrock, '_invoke_claude', return_value=json.dumps(mock_response)):
            report = service.generate_feed_efficiency_report(
                livestock_id=1,
                species="cattle",
                purpose="meat",
                start_weight_kg=200.0,
                current_weight_kg=250.0,
                days_elapsed=90,
                total_feed_cost_inr=9000.0
            )
            
            assert "efficiency_metrics" in report
            assert "benchmarks" in report
            assert "recommendations" in report
            assert report["efficiency_metrics"]["efficiency_rating"] == "Good"
            assert report["efficiency_metrics"]["avg_daily_gain_kg"] > 0
    
    def test_generate_feed_efficiency_report_poor_performance(self):
        """Test feed efficiency report for poor performance"""
        service = LivestockNutritionService()
        
        mock_response = {
            "efficiency_metrics": {
                "weight_gain_kg": 20.0,
                "avg_daily_gain_kg": 0.222,
                "cost_per_kg_gain_inr": 450.0,
                "feed_conversion_ratio": 12.0,
                "efficiency_rating": "Poor"
            },
            "benchmarks": {
                "industry_avg_daily_gain_kg": 0.500,
                "industry_avg_cost_per_kg_inr": 200.0,
                "performance_percentile": 20
            },
            "cost_analysis": {
                "total_feed_cost_inr": 9000.0,
                "cost_efficiency_rating": "Poor",
                "potential_savings_inr": 4000,
                "potential_savings_percentage": 44.4
            },
            "recommendations": [
                {
                    "category": "Health Check",
                    "recommendation": "Consult veterinarian for health issues",
                    "expected_impact": "Identify underlying health problems",
                    "priority": "High"
                },
                {
                    "category": "Feed Quality",
                    "recommendation": "Improve feed quality and digestibility",
                    "expected_impact": "Improve FCR by 30%",
                    "priority": "High"
                }
            ],
            "projected_improvements": {
                "improved_daily_gain_kg": 0.444,
                "improved_cost_per_kg_inr": 225.0,
                "timeline_days": 60,
                "expected_savings_monthly_inr": 2000
            },
            "confidence_score": 0.80
        }
        
        with patch.object(service.bedrock, '_invoke_claude', return_value=json.dumps(mock_response)):
            report = service.generate_feed_efficiency_report(
                livestock_id=2,
                species="cattle",
                purpose="meat",
                start_weight_kg=200.0,
                current_weight_kg=220.0,
                days_elapsed=90,
                total_feed_cost_inr=9000.0
            )
            
            assert report["efficiency_metrics"]["efficiency_rating"] == "Poor"
            assert len(report["recommendations"]) > 0
            assert any(r["priority"] == "High" for r in report["recommendations"])
    
    def test_feed_efficiency_with_milk_production(self):
        """Test feed efficiency report for dairy cattle"""
        service = LivestockNutritionService()
        
        mock_response = {
            "efficiency_metrics": {
                "weight_gain_kg": 10.0,
                "avg_daily_gain_kg": 0.111,
                "cost_per_kg_gain_inr": 900.0,
                "feed_conversion_ratio": 15.0,
                "efficiency_rating": "Good"
            },
            "benchmarks": {
                "industry_avg_daily_gain_kg": 0.100,
                "industry_avg_cost_per_kg_inr": 1000.0,
                "performance_percentile": 60
            },
            "cost_analysis": {
                "total_feed_cost_inr": 9000.0,
                "cost_efficiency_rating": "Good",
                "potential_savings_inr": 300,
                "potential_savings_percentage": 3.3
            },
            "recommendations": [
                {
                    "category": "Milk Production",
                    "recommendation": "Maintain current feeding program",
                    "expected_impact": "Sustain milk production",
                    "priority": "Low"
                }
            ],
            "projected_improvements": {
                "improved_daily_gain_kg": 0.122,
                "improved_cost_per_kg_inr": 870.0,
                "timeline_days": 30,
                "expected_savings_monthly_inr": 300
            },
            "confidence_score": 0.85
        }
        
        with patch.object(service.bedrock, '_invoke_claude', return_value=json.dumps(mock_response)):
            report = service.generate_feed_efficiency_report(
                livestock_id=3,
                species="cattle",
                purpose="dairy",
                start_weight_kg=440.0,
                current_weight_kg=450.0,
                days_elapsed=90,
                total_feed_cost_inr=9000.0,
                milk_production_liters=12.0
            )
            
            assert "efficiency_metrics" in report
            assert report["efficiency_metrics"]["efficiency_rating"] == "Good"


class TestNutritionServiceIntegration:
    """Integration tests for nutrition service"""
    
    def test_singleton_instance(self):
        """Test that nutrition_service is a singleton"""
        assert nutrition_service is not None
        assert isinstance(nutrition_service, LivestockNutritionService)
    
    def test_bedrock_integration(self):
        """Test that service has Bedrock integration"""
        service = LivestockNutritionService()
        assert service.bedrock is not None
    
    @pytest.mark.parametrize("species,age_months,expected_stage", [
        ("cattle", 3, "calf"),
        ("cattle", 12, "growing"),
        ("cattle", 24, "adult"),
        ("goat", 2, "kid"),
        ("goat", 8, "growing"),
        ("goat", 15, "adult"),
        ("poultry", 1, "chick"),
        ("poultry", 3, "growing"),
        ("poultry", 6, "adult"),
    ])
    def test_growth_stage_determination(self, species, age_months, expected_stage):
        """Test growth stage determination for different species and ages"""
        service = LivestockNutritionService()
        stage = service._determine_growth_stage(species, age_months, None)
        assert stage == expected_stage


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
