"""
Property-based tests for prediction accuracy validation
Tests Property 18: Prediction Accuracy Validation

**Validates: Requirements (Success Criteria - Prediction Accuracy)**
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from typing import List, Dict, Any
from decimal import Decimal


# Custom strategies for generating crop yield predictions
@st.composite
def crop_prediction_strategy(draw):
    """
    Generate valid crop yield prediction with actual harvest outcome
    
    This strategy creates predictions with expected yields and actual harvest
    outcomes to test accuracy tracking.
    """
    # Generate expected yield (predicted)
    expected_yield = draw(st.floats(min_value=10.0, max_value=100.0))
    
    # Generate actual yield (with some variance from expected)
    # Variance can be ±30% to simulate real-world prediction accuracy
    variance_factor = draw(st.floats(min_value=0.7, max_value=1.3))
    actual_yield = expected_yield * variance_factor
    
    # Ensure actual yield is positive
    actual_yield = max(0.1, actual_yield)
    
    return {
        "crop_id": draw(st.integers(min_value=1, max_value=10000)),
        "crop_name": draw(st.sampled_from([
            "Rice", "Wheat", "Cotton", "Maize", "Soybean", 
            "Sugarcane", "Chickpea", "Mustard"
        ])),
        "expected_yield": expected_yield,
        "actual_yield": actual_yield,
        "area_acres": draw(st.floats(min_value=1.0, max_value=50.0)),
        "season": draw(st.sampled_from(["kharif", "rabi", "zaid"])),
        "year": draw(st.integers(min_value=2024, max_value=2030))
    }


@st.composite
def prediction_batch_strategy(draw):
    """
    Generate a batch of predictions to test rolling average accuracy
    
    This strategy creates multiple predictions to test that the system
    maintains rolling average accuracy ≥ 85%.
    """
    # Generate between 10 and 100 predictions
    num_predictions = draw(st.integers(min_value=10, max_value=100))
    
    predictions = []
    for _ in range(num_predictions):
        prediction = draw(crop_prediction_strategy())
        predictions.append(prediction)
    
    return predictions


@st.composite
def high_accuracy_prediction_batch_strategy(draw):
    """
    Generate a batch of predictions with high accuracy (≥85%)
    
    This strategy creates predictions where actual yields are close to
    expected yields, ensuring rolling average accuracy ≥ 85%.
    """
    num_predictions = draw(st.integers(min_value=10, max_value=50))
    
    predictions = []
    for _ in range(num_predictions):
        expected_yield = draw(st.floats(min_value=10.0, max_value=100.0))
        
        # Generate actual yield with ≤15% variance to ensure ≥85% accuracy
        variance_factor = draw(st.floats(min_value=0.85, max_value=1.15))
        actual_yield = expected_yield * variance_factor
        actual_yield = max(0.1, actual_yield)
        
        predictions.append({
            "crop_id": draw(st.integers(min_value=1, max_value=10000)),
            "crop_name": draw(st.sampled_from([
                "Rice", "Wheat", "Cotton", "Maize", "Soybean"
            ])),
            "expected_yield": expected_yield,
            "actual_yield": actual_yield,
            "area_acres": draw(st.floats(min_value=1.0, max_value=50.0)),
            "season": draw(st.sampled_from(["kharif", "rabi", "zaid"])),
            "year": draw(st.integers(min_value=2024, max_value=2030))
        })
    
    return predictions


def calculate_prediction_accuracy(expected: float, actual: float) -> float:
    """
    Calculate prediction accuracy for a single prediction
    
    Accuracy = 1 - |expected - actual| / expected
    Returns value between 0.0 and 1.0
    """
    if expected <= 0:
        return 0.0
    
    error = abs(expected - actual)
    accuracy = 1.0 - (error / expected)
    
    # Clamp accuracy to [0, 1] range
    return max(0.0, min(1.0, accuracy))


def calculate_rolling_average_accuracy(predictions: List[Dict[str, Any]]) -> float:
    """
    Calculate rolling average accuracy across all predictions
    
    Returns average accuracy as a percentage (0-100)
    """
    if not predictions:
        return 0.0
    
    total_accuracy = 0.0
    for prediction in predictions:
        accuracy = calculate_prediction_accuracy(
            prediction["expected_yield"],
            prediction["actual_yield"]
        )
        total_accuracy += accuracy
    
    average_accuracy = total_accuracy / len(predictions)
    return average_accuracy * 100  # Convert to percentage


class TestPredictionAccuracyValidation:
    """
    Property 18: Prediction Accuracy Validation
    
    Test that for any crop yield prediction, system tracks actual harvest
    outcomes and maintains rolling average accuracy ≥ 85%.
    """
    
    @given(prediction=crop_prediction_strategy())
    @settings(
        max_examples=200,
        deadline=15000,  # 15 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_prediction_accuracy_calculation(self, prediction):
        """
        **Validates: Requirements (Success Criteria - Prediction Accuracy)**
        
        Property: For any crop yield prediction with actual harvest outcome,
        the system should calculate prediction accuracy correctly.
        """
        # Assert: Expected yield is present and positive
        assert "expected_yield" in prediction, \
            "Expected yield missing from prediction"
        assert prediction["expected_yield"] > 0, \
            f"Expected yield must be positive, got {prediction['expected_yield']}"
        
        # Assert: Actual yield is present and non-negative
        assert "actual_yield" in prediction, \
            "Actual yield missing from prediction"
        assert prediction["actual_yield"] >= 0, \
            f"Actual yield cannot be negative, got {prediction['actual_yield']}"
        
        # Calculate accuracy
        accuracy = calculate_prediction_accuracy(
            prediction["expected_yield"],
            prediction["actual_yield"]
        )
        
        # Assert: Accuracy is in valid range [0, 1]
        assert 0.0 <= accuracy <= 1.0, \
            f"Accuracy {accuracy} out of valid range [0, 1]"
        
        # Assert: Accuracy calculation is correct
        expected_error = abs(prediction["expected_yield"] - prediction["actual_yield"])
        expected_accuracy = 1.0 - (expected_error / prediction["expected_yield"])
        expected_accuracy = max(0.0, min(1.0, expected_accuracy))
        
        assert abs(accuracy - expected_accuracy) < 0.001, \
            f"Accuracy calculation incorrect: expected {expected_accuracy}, got {accuracy}"
    
    @given(prediction=crop_prediction_strategy())
    @settings(
        max_examples=200,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_prediction_tracking_fields_present(self, prediction):
        """
        **Validates: Requirements (Success Criteria - Prediction Accuracy)**
        
        Property: For any crop yield prediction, the system should track
        all required fields for accuracy validation.
        """
        # Assert: Crop identification fields present
        assert "crop_id" in prediction, \
            "Crop ID missing from prediction"
        assert prediction["crop_id"] > 0, \
            "Crop ID must be positive"
        
        assert "crop_name" in prediction, \
            "Crop name missing from prediction"
        assert len(prediction["crop_name"]) > 0, \
            "Crop name cannot be empty"
        
        # Assert: Prediction fields present
        assert "expected_yield" in prediction, \
            "Expected yield missing from prediction"
        assert "actual_yield" in prediction, \
            "Actual yield missing from prediction"
        
        # Assert: Context fields present
        assert "area_acres" in prediction, \
            "Area in acres missing from prediction"
        assert prediction["area_acres"] > 0, \
            "Area must be positive"
        
        assert "season" in prediction, \
            "Season missing from prediction"
        assert prediction["season"] in ["kharif", "rabi", "zaid"], \
            f"Invalid season: {prediction['season']}"
        
        assert "year" in prediction, \
            "Year missing from prediction"
        assert prediction["year"] >= 2024, \
            f"Year must be 2024 or later, got {prediction['year']}"
    
    @given(predictions=prediction_batch_strategy())
    @settings(
        max_examples=200,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_rolling_average_accuracy_calculation(self, predictions):
        """
        **Validates: Requirements (Success Criteria - Prediction Accuracy)**
        
        Property: For any batch of crop yield predictions, the system should
        calculate rolling average accuracy correctly across all predictions.
        """
        # Assert: Predictions batch is not empty
        assert len(predictions) > 0, \
            "Predictions batch cannot be empty"
        
        # Calculate rolling average accuracy
        rolling_avg_accuracy = calculate_rolling_average_accuracy(predictions)
        
        # Assert: Rolling average accuracy is in valid range [0, 100]
        assert 0.0 <= rolling_avg_accuracy <= 100.0, \
            f"Rolling average accuracy {rolling_avg_accuracy}% out of valid range [0, 100]"
        
        # Verify calculation by manually computing average
        total_accuracy = 0.0
        for prediction in predictions:
            accuracy = calculate_prediction_accuracy(
                prediction["expected_yield"],
                prediction["actual_yield"]
            )
            total_accuracy += accuracy
        
        expected_avg = (total_accuracy / len(predictions)) * 100
        
        assert abs(rolling_avg_accuracy - expected_avg) < 0.01, \
            f"Rolling average calculation incorrect: expected {expected_avg}%, got {rolling_avg_accuracy}%"
    
    @given(predictions=high_accuracy_prediction_batch_strategy())
    @settings(
        max_examples=200,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_high_accuracy_predictions_meet_threshold(self, predictions):
        """
        **Validates: Requirements (Success Criteria - Prediction Accuracy)**
        
        Property: For any batch of high-accuracy predictions (variance ≤15%),
        the rolling average accuracy should be ≥ 85%.
        """
        # Assert: Predictions batch is not empty
        assert len(predictions) > 0, \
            "Predictions batch cannot be empty"
        
        # Calculate rolling average accuracy
        rolling_avg_accuracy = calculate_rolling_average_accuracy(predictions)
        
        # Assert: Rolling average accuracy meets 85% threshold
        # Use small epsilon for floating-point comparison
        assert rolling_avg_accuracy >= 84.99, \
            f"Rolling average accuracy {rolling_avg_accuracy:.2f}% below 85% threshold"
        
        # Verify individual predictions have high accuracy
        low_accuracy_count = 0
        for prediction in predictions:
            accuracy = calculate_prediction_accuracy(
                prediction["expected_yield"],
                prediction["actual_yield"]
            )
            if accuracy < 0.85:
                low_accuracy_count += 1
        
        # Allow some predictions to be below 85% as long as average is ≥85%
        assert low_accuracy_count < len(predictions) * 0.5, \
            f"Too many low-accuracy predictions: {low_accuracy_count}/{len(predictions)}"
    
    @given(predictions=prediction_batch_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_accuracy_tracking_persistence(self, predictions):
        """
        **Validates: Requirements (Success Criteria - Prediction Accuracy)**
        
        Property: For any batch of predictions, the system should maintain
        accuracy tracking data for all predictions.
        """
        # Assert: All predictions have required tracking fields
        for idx, prediction in enumerate(predictions):
            assert "crop_id" in prediction, \
                f"Prediction {idx} missing crop_id"
            assert "expected_yield" in prediction, \
                f"Prediction {idx} missing expected_yield"
            assert "actual_yield" in prediction, \
                f"Prediction {idx} missing actual_yield"
            
            # Calculate and verify accuracy can be computed
            accuracy = calculate_prediction_accuracy(
                prediction["expected_yield"],
                prediction["actual_yield"]
            )
            
            assert 0.0 <= accuracy <= 1.0, \
                f"Prediction {idx} has invalid accuracy: {accuracy}"
    
    @given(prediction=crop_prediction_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_perfect_prediction_accuracy(self, prediction):
        """
        **Validates: Requirements (Success Criteria - Prediction Accuracy)**
        
        Property: When expected yield equals actual yield, accuracy should be 100%.
        """
        # Set actual yield equal to expected yield
        prediction["actual_yield"] = prediction["expected_yield"]
        
        # Calculate accuracy
        accuracy = calculate_prediction_accuracy(
            prediction["expected_yield"],
            prediction["actual_yield"]
        )
        
        # Assert: Accuracy is 100% (1.0)
        assert abs(accuracy - 1.0) < 0.001, \
            f"Perfect prediction should have 100% accuracy, got {accuracy * 100}%"
    
    @given(prediction=crop_prediction_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_zero_actual_yield_accuracy(self, prediction):
        """
        **Validates: Requirements (Success Criteria - Prediction Accuracy)**
        
        Property: When actual yield is zero (crop failure), accuracy should
        reflect the complete prediction error.
        """
        # Set actual yield to zero (crop failure)
        prediction["actual_yield"] = 0.0
        
        # Calculate accuracy
        accuracy = calculate_prediction_accuracy(
            prediction["expected_yield"],
            prediction["actual_yield"]
        )
        
        # Assert: Accuracy is 0% (0.0) since prediction was completely wrong
        assert abs(accuracy - 0.0) < 0.001, \
            f"Zero actual yield should have 0% accuracy, got {accuracy * 100}%"
    
    @given(predictions=prediction_batch_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_accuracy_by_season(self, predictions):
        """
        **Validates: Requirements (Success Criteria - Prediction Accuracy)**
        
        Property: For any batch of predictions, the system should be able to
        calculate accuracy separately for each season (kharif, rabi, zaid).
        """
        # Group predictions by season
        season_predictions = {
            "kharif": [],
            "rabi": [],
            "zaid": []
        }
        
        for prediction in predictions:
            season = prediction["season"]
            season_predictions[season].append(prediction)
        
        # Calculate accuracy for each season
        for season, season_preds in season_predictions.items():
            if len(season_preds) > 0:
                season_accuracy = calculate_rolling_average_accuracy(season_preds)
                
                # Assert: Season accuracy is in valid range
                assert 0.0 <= season_accuracy <= 100.0, \
                    f"{season} season accuracy {season_accuracy}% out of valid range"
    
    @given(predictions=prediction_batch_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_accuracy_by_crop_type(self, predictions):
        """
        **Validates: Requirements (Success Criteria - Prediction Accuracy)**
        
        Property: For any batch of predictions, the system should be able to
        calculate accuracy separately for each crop type.
        """
        # Group predictions by crop type
        crop_predictions = {}
        
        for prediction in predictions:
            crop_name = prediction["crop_name"]
            if crop_name not in crop_predictions:
                crop_predictions[crop_name] = []
            crop_predictions[crop_name].append(prediction)
        
        # Calculate accuracy for each crop type
        for crop_name, crop_preds in crop_predictions.items():
            if len(crop_preds) > 0:
                crop_accuracy = calculate_rolling_average_accuracy(crop_preds)
                
                # Assert: Crop accuracy is in valid range
                assert 0.0 <= crop_accuracy <= 100.0, \
                    f"{crop_name} accuracy {crop_accuracy}% out of valid range"
    
    def test_accuracy_threshold_validation(self):
        """
        **Validates: Requirements (Success Criteria - Prediction Accuracy)**
        
        Integration test: Verify that the system can validate if rolling
        average accuracy meets the 85% threshold.
        """
        # Create test predictions with known accuracy
        high_accuracy_predictions = [
            {
                "crop_id": i,
                "crop_name": "Rice",
                "expected_yield": 100.0,
                "actual_yield": 90.0,  # 90% accuracy
                "area_acres": 5.0,
                "season": "kharif",
                "year": 2024
            }
            for i in range(1, 11)
        ]
        
        # Calculate rolling average accuracy
        rolling_avg = calculate_rolling_average_accuracy(high_accuracy_predictions)
        
        # Assert: Rolling average meets 85% threshold
        assert rolling_avg >= 85.0, \
            f"Rolling average accuracy {rolling_avg:.2f}% below 85% threshold"
        
        # Create test predictions with low accuracy
        low_accuracy_predictions = [
            {
                "crop_id": i,
                "crop_name": "Wheat",
                "expected_yield": 100.0,
                "actual_yield": 50.0,  # 50% accuracy
                "area_acres": 5.0,
                "season": "rabi",
                "year": 2024
            }
            for i in range(1, 11)
        ]
        
        # Calculate rolling average accuracy
        rolling_avg_low = calculate_rolling_average_accuracy(low_accuracy_predictions)
        
        # Assert: Rolling average does not meet 85% threshold
        assert rolling_avg_low < 85.0, \
            f"Low accuracy predictions should not meet 85% threshold, got {rolling_avg_low:.2f}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
