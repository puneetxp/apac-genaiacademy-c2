"""
Unit tests for Hybrid AI Service

Tests intelligent routing between SageMaker and Bedrock,
cost optimization, caching, and fallback mechanisms.

Validates: Requirements AC14 (Phase 9 - Required)
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, UTC

from app.services.hybrid_ai_service import (
    HybridAIService,
    QueryType,
    ModelType
)
from app.core.model_router import ModelRouter, RoutingStrategy


class TestHybridAIService:
    """Test suite for HybridAIService"""
    
    @pytest.fixture
    def hybrid_service(self):
        """Create hybrid AI service instance"""
        return HybridAIService()
    
    @pytest.fixture
    def sample_yield_request(self):
        """Sample yield prediction request"""
        return {
            "crop_name": "Rice",
            "variety": "Basmati",
            "state": "Punjab",
            "district": "Ludhiana",
            "planting_date": "2024-06-15",
            "area_acres": 5.0,
            "soil_type": "loamy",
            "irrigation_type": "canal"
        }
    
    # ==================== Query Classification Tests ====================
    
    def test_classify_yield_prediction_to_sagemaker(self, hybrid_service):
        """Test that yield predictions route to SageMaker when available"""
        # Enable SageMaker for this test
        hybrid_service.sagemaker_enabled = True
        
        model_type = hybrid_service.classify_query(
            QueryType.YIELD_PREDICTION,
            has_training_data=True
        )
        
        assert model_type == ModelType.SAGEMAKER
    
    def test_classify_yield_prediction_to_bedrock_no_data(self, hybrid_service):
        """Test that yield predictions route to Bedrock without training data"""
        model_type = hybrid_service.classify_query(
            QueryType.YIELD_PREDICTION,
            has_training_data=False
        )
        
        assert model_type == ModelType.BEDROCK
    
    def test_classify_annual_strategy_to_bedrock(self, hybrid_service):
        """Test that annual strategy always routes to Bedrock"""
        model_type = hybrid_service.classify_query(
            QueryType.ANNUAL_STRATEGY,
            has_training_data=True
        )
        
        assert model_type == ModelType.BEDROCK
    
    def test_classify_crop_recommendation_to_bedrock(self, hybrid_service):
        """Test that crop recommendations route to Bedrock"""
        model_type = hybrid_service.classify_query(
            QueryType.CROP_RECOMMENDATION,
            has_training_data=True
        )
        
        assert model_type == ModelType.BEDROCK
    
    def test_classify_market_analysis_to_bedrock(self, hybrid_service):
        """Test that market analysis routes to Bedrock"""
        model_type = hybrid_service.classify_query(
            QueryType.MARKET_ANALYSIS,
            has_training_data=True
        )
        
        assert model_type == ModelType.BEDROCK
    
    # ==================== Yield Prediction Tests ====================
    
    @pytest.mark.asyncio
    async def test_predict_yield_with_sagemaker(self, hybrid_service, sample_yield_request):
        """Test yield prediction using SageMaker"""
        with patch.object(hybrid_service, '_predict_yield_sagemaker', new_callable=AsyncMock) as mock_sagemaker:
            mock_sagemaker.return_value = {
                "expected_yield_per_acre": 25.5,
                "yield_range": {"min": 23.0, "max": 28.0},
                "total_expected_yield": 127.5,
                "confidence_score": 0.93,
                "model_accuracy": "92-95%",
                "prediction_method": "SageMaker Custom ML Model"
            }
            
            result = await hybrid_service.predict_crop_yield(
                **sample_yield_request,
                force_model=ModelType.SAGEMAKER
            )
            
            assert result["model_used"] == ModelType.SAGEMAKER.value
            assert result["expected_yield_per_acre"] == 25.5
            assert result["confidence_score"] == 0.93
            assert result["model_accuracy"] == "92-95%"
            assert "timestamp" in result
            assert "cost_estimate_inr" in result
            mock_sagemaker.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_predict_yield_with_bedrock(self, hybrid_service, sample_yield_request):
        """Test yield prediction using Bedrock"""
        with patch.object(hybrid_service, '_predict_yield_bedrock', new_callable=AsyncMock) as mock_bedrock:
            mock_bedrock.return_value = {
                "expected_yield_per_acre": 24.0,
                "yield_range": {"min": 22.0, "max": 26.0},
                "total_expected_yield": 120.0,
                "confidence_score": 0.87,
                "model_accuracy": "85-90%",
                "prediction_method": "Bedrock Foundation Model"
            }
            
            result = await hybrid_service.predict_crop_yield(
                **sample_yield_request,
                force_model=ModelType.BEDROCK
            )
            
            assert result["model_used"] == ModelType.BEDROCK.value
            assert result["expected_yield_per_acre"] == 24.0
            assert result["confidence_score"] == 0.87
            assert result["model_accuracy"] == "85-90%"
            assert "timestamp" in result
            assert "cost_estimate_inr" in result
            mock_bedrock.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_predict_yield_fallback_to_bedrock(self, hybrid_service, sample_yield_request):
        """Test fallback to Bedrock when SageMaker fails"""
        with patch.object(hybrid_service, '_predict_yield_sagemaker', new_callable=AsyncMock) as mock_sagemaker, \
             patch.object(hybrid_service, '_predict_yield_bedrock', new_callable=AsyncMock) as mock_bedrock:
            
            # SageMaker fails
            mock_sagemaker.side_effect = Exception("SageMaker endpoint unavailable")
            
            # Bedrock succeeds
            mock_bedrock.return_value = {
                "expected_yield_per_acre": 24.0,
                "confidence_score": 0.87,
                "model_accuracy": "85-90%",
                "prediction_method": "Bedrock Foundation Model"
            }
            
            result = await hybrid_service.predict_crop_yield(
                **sample_yield_request,
                force_model=ModelType.SAGEMAKER
            )
            
            assert result["model_used"] == ModelType.BEDROCK.value
            assert result["fallback"] == True
            assert result["expected_yield_per_acre"] == 24.0
            mock_sagemaker.assert_called_once()
            mock_bedrock.assert_called_once()
    
    # ==================== Annual Strategy Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_annual_strategy(self, hybrid_service):
        """Test annual strategy generation using Bedrock"""
        with patch('app.services.hybrid_ai_service.bedrock_service') as mock_bedrock:
            mock_bedrock.get_annual_crop_strategy.return_value = {
                "kharif": {
                    "recommended_crop": "Rice",
                    "expected_profit_per_acre": 40000,
                    "confidence_score": 0.88
                },
                "rabi": {
                    "recommended_crop": "Wheat",
                    "expected_profit_per_acre": 35000,
                    "confidence_score": 0.85
                },
                "annual_summary": {
                    "total_expected_profit_per_acre": 75000
                }
            }
            
            result = await hybrid_service.get_annual_strategy(
                state="Punjab",
                district="Ludhiana",
                soil_type="loamy",
                area_acres=5.0,
                irrigation_type="canal"
            )
            
            assert result["model_used"] == ModelType.BEDROCK.value
            assert result["kharif"]["recommended_crop"] == "Rice"
            assert result["rabi"]["recommended_crop"] == "Wheat"
            assert "timestamp" in result
            assert "cost_estimate_inr" in result
            mock_bedrock.get_annual_crop_strategy.assert_called_once()
    
    # ==================== Crop Recommendations Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_crop_recommendations(self, hybrid_service):
        """Test crop recommendations using Bedrock"""
        with patch('app.services.hybrid_ai_service.bedrock_service') as mock_bedrock:
            mock_bedrock.get_crop_recommendations.return_value = [
                {
                    "rank": 1,
                    "crop_name": "Rice",
                    "expected_profit_per_acre": 40000,
                    "confidence_score": 0.88
                },
                {
                    "rank": 2,
                    "crop_name": "Cotton",
                    "expected_profit_per_acre": 35000,
                    "confidence_score": 0.85
                }
            ]
            
            result = await hybrid_service.get_crop_recommendations(
                state="Punjab",
                district="Ludhiana",
                season="kharif",
                soil_type="loamy",
                area_acres=5.0,
                irrigation_type="canal"
            )
            
            assert len(result) == 2
            assert result[0]["crop_name"] == "Rice"
            assert result[0]["model_used"] == ModelType.BEDROCK.value
            assert "timestamp" in result[0]
            mock_bedrock.get_crop_recommendations.assert_called_once()
    
    # ==================== Batch Inference Tests ====================
    
    @pytest.mark.asyncio
    async def test_batch_predict_yields(self, hybrid_service, sample_yield_request):
        """Test batch inference for multiple predictions"""
        predictions = [
            sample_yield_request,
            {**sample_yield_request, "crop_name": "Wheat"},
            {**sample_yield_request, "crop_name": "Cotton"}
        ]
        
        with patch.object(hybrid_service, 'predict_crop_yield', new_callable=AsyncMock) as mock_predict:
            mock_predict.return_value = {
                "expected_yield_per_acre": 25.0,
                "confidence_score": 0.90,
                "model_used": "sagemaker"
            }
            
            results = await hybrid_service.batch_predict_yields(
                predictions=predictions,
                use_sagemaker=True
            )
            
            assert len(results) == 3
            assert all("expected_yield_per_acre" in r for r in results)
            assert mock_predict.call_count == 3
    
    # ==================== Cost Optimization Tests ====================
    
    def test_calculate_cost_sagemaker(self, hybrid_service):
        """Test cost calculation for SageMaker"""
        cost = hybrid_service._calculate_cost(ModelType.SAGEMAKER)
        
        # SageMaker: $0.002 * 83 = ~₹0.17
        assert cost < 1.0  # Should be less than ₹1
        assert cost > 0.1  # Should be more than ₹0.1
    
    def test_calculate_cost_bedrock(self, hybrid_service):
        """Test cost calculation for Bedrock"""
        cost = hybrid_service._calculate_cost(ModelType.BEDROCK)
        
        # Bedrock: $0.05 * 83 = ~₹4.15
        assert cost > 4.0  # Should be more than ₹4
        assert cost < 5.0  # Should be less than ₹5
    
    def test_get_cost_report(self, hybrid_service):
        """Test cost report generation"""
        # Simulate some calls
        hybrid_service.model_performance[ModelType.SAGEMAKER]["calls"] = 100
        hybrid_service.model_performance[ModelType.BEDROCK]["calls"] = 50
        
        report = hybrid_service.get_cost_report()
        
        assert report["total_calls"] == 150
        assert report["sagemaker_calls"] == 100
        assert report["bedrock_calls"] == 50
        assert report["total_cost_inr"] > 0
        assert report["cost_per_prediction_inr"] > 0
        assert report["savings_vs_bedrock_only_inr"] > 0
        assert report["savings_percentage"] > 0
        assert "meets_target" in report
    
    def test_cost_target_achievement(self, hybrid_service):
        """Test that hybrid approach meets cost target (< ₹3 per prediction)"""
        # Simulate realistic usage: 70% SageMaker, 30% Bedrock
        hybrid_service.model_performance[ModelType.SAGEMAKER]["calls"] = 700
        hybrid_service.model_performance[ModelType.BEDROCK]["calls"] = 300
        
        report = hybrid_service.get_cost_report()
        
        # With 70% SageMaker (₹0.17) and 30% Bedrock (₹4.15):
        # Average cost = 0.7 * 0.17 + 0.3 * 4.15 = 0.119 + 1.245 = ₹1.364
        assert report["cost_per_prediction_inr"] < 3.0
        assert report["meets_target"] == True
    
    # ==================== Performance Monitoring Tests ====================
    
    def test_log_routing_decision(self, hybrid_service):
        """Test routing decision logging"""
        initial_count = len(hybrid_service.routing_decisions)
        
        hybrid_service._log_routing_decision(
            QueryType.YIELD_PREDICTION,
            ModelType.SAGEMAKER
        )
        
        assert len(hybrid_service.routing_decisions) == initial_count + 1
        decision = hybrid_service.routing_decisions[-1]
        assert decision["query_type"] == QueryType.YIELD_PREDICTION.value
        assert decision["model_type"] == ModelType.SAGEMAKER.value
        assert "timestamp" in decision
    
    def test_get_performance_report(self, hybrid_service):
        """Test performance report generation"""
        # Simulate some calls and errors
        hybrid_service.model_performance[ModelType.SAGEMAKER]["calls"] = 100
        hybrid_service.model_performance[ModelType.SAGEMAKER]["errors"] = 2
        hybrid_service.model_performance[ModelType.BEDROCK]["calls"] = 50
        hybrid_service.model_performance[ModelType.BEDROCK]["errors"] = 1
        
        report = hybrid_service.get_performance_report()
        
        assert report["total_calls"] == 150
        assert report["total_errors"] == 3
        assert report["routing_accuracy"] > 95.0  # (147/150) * 100 = 98%
        assert report["sagemaker_performance"]["calls"] == 100
        assert report["sagemaker_performance"]["errors"] == 2
        assert report["bedrock_performance"]["calls"] == 50
        assert report["bedrock_performance"]["errors"] == 1
        assert "cache_hit_rate" in report
        assert report["fallback_success_rate"] == 100.0
        assert "meets_target" in report
    
    def test_routing_accuracy_target(self, hybrid_service):
        """Test that routing accuracy meets target (> 98%)"""
        # Simulate high success rate
        hybrid_service.model_performance[ModelType.SAGEMAKER]["calls"] = 500
        hybrid_service.model_performance[ModelType.SAGEMAKER]["errors"] = 5
        hybrid_service.model_performance[ModelType.BEDROCK]["calls"] = 500
        hybrid_service.model_performance[ModelType.BEDROCK]["errors"] = 5
        
        report = hybrid_service.get_performance_report()
        
        # (990/1000) * 100 = 99%
        assert report["routing_accuracy"] >= 98.0
        assert report["meets_target"] == True
    
    def test_get_routing_statistics(self, hybrid_service):
        """Test routing statistics by query type"""
        # Simulate routing decisions
        hybrid_service._log_routing_decision(QueryType.YIELD_PREDICTION, ModelType.SAGEMAKER)
        hybrid_service._log_routing_decision(QueryType.YIELD_PREDICTION, ModelType.SAGEMAKER)
        hybrid_service._log_routing_decision(QueryType.ANNUAL_STRATEGY, ModelType.BEDROCK)
        hybrid_service._log_routing_decision(QueryType.CROP_RECOMMENDATION, ModelType.BEDROCK)
        
        stats = hybrid_service.get_routing_statistics()
        
        assert QueryType.YIELD_PREDICTION.value in stats
        assert stats[QueryType.YIELD_PREDICTION.value][ModelType.SAGEMAKER.value] == 2
        assert stats[QueryType.ANNUAL_STRATEGY.value][ModelType.BEDROCK.value] == 1
        assert stats[QueryType.CROP_RECOMMENDATION.value][ModelType.BEDROCK.value] == 1


class TestModelRouter:
    """Test suite for ModelRouter"""
    
    @pytest.fixture
    def router(self):
        """Create model router instance"""
        return ModelRouter(strategy=RoutingStrategy.BALANCED)
    
    # ==================== Routing Strategy Tests ====================
    
    def test_route_yield_prediction_balanced(self, router):
        """Test balanced routing for yield prediction"""
        model, metadata = router.route_query(
            query_type="yield_prediction",
            has_training_data=True,
            training_samples=200,
            sagemaker_available=True
        )
        
        assert model == "sagemaker"
        assert "reason" in metadata
        assert "confidence" in metadata
        assert metadata["confidence"] >= 0.9
    
    def test_route_crop_recommendation_balanced(self, router):
        """Test balanced routing for crop recommendation"""
        model, metadata = router.route_query(
            query_type="crop_recommendation",
            has_training_data=True,
            sagemaker_available=True
        )
        
        assert model == "bedrock"
        assert "reason" in metadata
        assert "confidence" in metadata
    
    def test_route_insufficient_training_data(self, router):
        """Test routing with insufficient training data"""
        model, metadata = router.route_query(
            query_type="yield_prediction",
            has_training_data=True,
            training_samples=50,  # Less than minimum (100)
            sagemaker_available=True
        )
        
        assert model == "bedrock"
        assert "Insufficient training data" in metadata["reason"]
    
    def test_route_sagemaker_unavailable(self, router):
        """Test routing when SageMaker is unavailable"""
        model, metadata = router.route_query(
            query_type="yield_prediction",
            has_training_data=True,
            training_samples=200,
            sagemaker_available=False
        )
        
        assert model == "bedrock"
        assert "unavailable" in metadata["reason"].lower()
    
    def test_accuracy_first_strategy(self):
        """Test accuracy-first routing strategy"""
        router = ModelRouter(strategy=RoutingStrategy.ACCURACY_FIRST)
        
        model, metadata = router.route_query(
            query_type="yield_prediction",
            has_training_data=True,
            training_samples=200,
            sagemaker_available=True
        )
        
        assert model == "sagemaker"
        assert "92-95%" in metadata.get("expected_accuracy", "")
    
    def test_cost_first_strategy_batch(self):
        """Test cost-first routing strategy for batch"""
        router = ModelRouter(strategy=RoutingStrategy.COST_FIRST)
        
        model, metadata = router.route_query(
            query_type="yield_prediction",
            has_training_data=True,
            training_samples=200,
            is_batch=True,
            sagemaker_available=True
        )
        
        assert model == "sagemaker"
        assert "batch" in metadata["reason"].lower()
    
    def test_cost_first_strategy_single(self):
        """Test cost-first routing strategy for single query"""
        router = ModelRouter(strategy=RoutingStrategy.COST_FIRST)
        
        model, metadata = router.route_query(
            query_type="yield_prediction",
            has_training_data=True,
            training_samples=200,
            is_batch=False,
            sagemaker_available=True
        )
        
        assert model == "bedrock"
        assert "single query" in metadata["reason"].lower()
    
    # ==================== Evaluation Tests ====================
    
    def test_evaluate_routing_decision_accuracy(self, router):
        """Test routing decision evaluation with accuracy"""
        evaluation = router.evaluate_routing_decision(
            model_used="sagemaker",
            actual_accuracy=0.94
        )
        
        assert evaluation["model_used"] == "sagemaker"
        assert evaluation["accuracy"]["actual"] == 0.94
        assert evaluation["accuracy"]["expected"] == router.sagemaker_accuracy_threshold
        assert evaluation["accuracy"]["meets_target"] == True
    
    def test_evaluate_routing_decision_cost(self, router):
        """Test routing decision evaluation with cost"""
        evaluation = router.evaluate_routing_decision(
            model_used="sagemaker",
            actual_cost=0.17
        )
        
        assert evaluation["cost"]["actual_inr"] == 0.17
        assert evaluation["cost"]["target_inr"] == 3.0
        assert evaluation["cost"]["meets_target"] == True
    
    def test_evaluate_routing_decision_latency(self, router):
        """Test routing decision evaluation with latency"""
        evaluation = router.evaluate_routing_decision(
            model_used="sagemaker",
            actual_latency_ms=450
        )
        
        assert evaluation["latency"]["actual_ms"] == 450
        assert evaluation["latency"]["target_ms"] == 500
        assert evaluation["latency"]["meets_target"] == True
    
    # ==================== Recommendation Tests ====================
    
    def test_get_routing_recommendation_no_history(self, router):
        """Test routing recommendation without historical data"""
        recommendation = router.get_routing_recommendation(
            query_type="yield_prediction"
        )
        
        assert "recommended_model" in recommendation
        assert "reason" in recommendation
        assert "confidence" in recommendation
    
    def test_get_routing_recommendation_with_history(self, router):
        """Test routing recommendation with historical performance"""
        historical_performance = {
            "sagemaker": {
                "accuracy": 0.94,
                "avg_cost_inr": 0.17
            },
            "bedrock": {
                "accuracy": 0.87,
                "avg_cost_inr": 4.15
            }
        }
        
        recommendation = router.get_routing_recommendation(
            query_type="yield_prediction",
            historical_performance=historical_performance
        )
        
        assert recommendation["recommended_model"] == "sagemaker"
        assert "value_scores" in recommendation
        assert recommendation["value_scores"]["sagemaker"] > recommendation["value_scores"]["bedrock"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
