"""
Test AI-powered supply matching engine with pgvector similarity search
Task 36.2: Build AI-powered supply matching engine
"""

from datetime import datetime, timedelta

import pytest

from app.services.supply_request_matching_service import SupplyRequestMatchingService


class TestSupplyMatchingPgVector:
    """Test pgvector-based supply matching functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.matching_service = SupplyRequestMatchingService()

    def test_embedding_generation_for_supply_request(self):
        """Test that embeddings are generated correctly for supply requests"""
        supply_request = {
            "id": 1,
            "crop_type": "wheat",
            "quality_requirements": "Grade A premium quality",
            "quantity_needed": 5000,
            "delivery_state": "Punjab",
            "delivery_district": "Ludhiana",
            "is_emergency": False,
        }

        embedding = self.matching_service._generate_request_embedding(supply_request)

        # Check embedding properties
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
        assert all(isinstance(x, float) for x in embedding)
        print(f"✓ Supply request embedding generated: {len(embedding)} dimensions")

    def test_embedding_generation_for_listing(self):
        """Test that embeddings are generated correctly for marketplace listings"""
        listing = {
            "id": 1,
            "crop_type": "wheat",
            "crop_variety": "HD-2967",
            "quality_grade": "A",
            "estimated_quantity": 6000,
            "available_quantity": 6000,
            "location_state": "Punjab",
            "location_district": "Ludhiana",
        }

        embedding = self.matching_service._generate_listing_embedding(listing)

        # Check embedding properties
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)
        print(f"✓ Listing embedding generated: {len(embedding)} dimensions")

    def test_cache_key_generation(self):
        """Test that cache keys are generated consistently"""
        data1 = {
            "crop_type": "wheat",
            "quality_requirements": "Grade A",
            "quantity_needed": 5000,
            "delivery_state": "Punjab",
            "delivery_district": "Ludhiana",
        }

        data2 = {
            "crop_type": "wheat",
            "quality_requirements": "Grade A",
            "quantity_needed": 5000,
            "delivery_state": "Punjab",
            "delivery_district": "Ludhiana",
        }

        key1 = self.matching_service._generate_cache_key(data1)
        key2 = self.matching_service._generate_cache_key(data2)

        assert key1 == key2
        assert len(key1) == 32  # MD5 hash length
        print(f"✓ Cache key generated consistently: {key1}")

    def test_distance_calculation(self):
        """Test GPS distance calculation using Haversine formula"""
        # Distance between Delhi and Mumbai (approx 1150 km)
        delhi_lat, delhi_lon = 28.6139, 77.2090
        mumbai_lat, mumbai_lon = 19.0760, 72.8777

        distance = self.matching_service._calculate_distance(
            delhi_lat, delhi_lon, mumbai_lat, mumbai_lon
        )

        assert distance is not None
        assert 1100 < distance < 1200  # Approximate distance
        print(f"✓ Distance calculated: {distance:.2f} km")

    def test_distance_calculation_with_missing_coords(self):
        """Test distance calculation returns None when coordinates missing"""
        distance = self.matching_service._calculate_distance(28.6139, 77.2090, None, None)

        assert distance is None
        print("✓ Distance calculation handles missing coordinates")

    def test_match_score_calculation_perfect_match(self):
        """Test match score calculation for a perfect match"""
        supply_request = {
            "crop_type": "wheat",
            "quality_requirements": "Grade A premium",
            "quantity_needed": 5000,
            "delivery_state": "Punjab",
            "delivery_district": "Ludhiana",
            "delivery_date_start": datetime.now() + timedelta(days=30),
            "delivery_date_end": datetime.now() + timedelta(days=45),
        }

        listing = {
            "id": 1,
            "crop_type": "wheat",
            "quality_grade": "A",
            "estimated_quantity": 6000,
            "available_quantity": 6000,
            "location_state": "Punjab",
            "location_district": "Ludhiana",
            "expected_harvest_date": datetime.now() + timedelta(days=35),
            "price_per_unit": 25.0,
        }

        vector_similarity = 0.95  # High similarity

        match_scores = self.matching_service._calculate_match_score(
            supply_request, listing, vector_similarity
        )

        assert match_scores["overall_score"] >= 85
        assert match_scores["component_scores"]["crop_match"] >= 90
        assert match_scores["component_scores"]["quality_match"] == 100
        assert match_scores["component_scores"]["quantity_match"] == 100
        assert match_scores["component_scores"]["location_proximity"] == 100
        assert match_scores["component_scores"]["timing_alignment"] == 100

        print(f"✓ Perfect match score: {match_scores['overall_score']:.2f}")
        print(f"  Component scores: {match_scores['component_scores']}")

    def test_match_score_calculation_partial_match(self):
        """Test match score calculation for a partial match"""
        supply_request = {
            "crop_type": "wheat",
            "quality_requirements": "Grade A",
            "quantity_needed": 10000,
            "delivery_state": "Punjab",
            "delivery_district": "Ludhiana",
            "delivery_date_start": datetime.now() + timedelta(days=30),
            "delivery_date_end": datetime.now() + timedelta(days=45),
        }

        listing = {
            "id": 1,
            "crop_type": "wheat",
            "quality_grade": "B",  # Lower quality
            "estimated_quantity": 5000,  # Half quantity
            "available_quantity": 5000,
            "location_state": "Punjab",
            "location_district": "Amritsar",  # Different district
            "expected_harvest_date": datetime.now() + timedelta(days=35),
            "price_per_unit": 25.0,
        }

        vector_similarity = 0.75

        match_scores = self.matching_service._calculate_match_score(
            supply_request, listing, vector_similarity
        )

        assert 50 <= match_scores["overall_score"] < 85
        assert match_scores["component_scores"]["quality_match"] < 100
        assert match_scores["component_scores"]["quantity_match"] < 100
        assert match_scores["component_scores"]["location_proximity"] < 100

        print(f"✓ Partial match score: {match_scores['overall_score']:.2f}")
        print(f"  Component scores: {match_scores['component_scores']}")

    def test_match_score_with_gps_distance(self):
        """Test match score calculation with GPS-based distance"""
        supply_request = {
            "crop_type": "wheat",
            "quality_requirements": "Grade A",
            "quantity_needed": 5000,
            "delivery_latitude": 28.6139,  # Delhi
            "delivery_longitude": 77.2090,
            "delivery_state": "Delhi",
            "delivery_district": "Central Delhi",
            "delivery_date_start": datetime.now() + timedelta(days=30),
            "delivery_date_end": datetime.now() + timedelta(days=45),
        }

        listing = {
            "id": 1,
            "crop_type": "wheat",
            "quality_grade": "A",
            "estimated_quantity": 6000,
            "available_quantity": 6000,
            "delivery_latitude": 28.7041,  # Nearby location (10 km)
            "delivery_longitude": 77.1025,
            "location_state": "Delhi",
            "location_district": "North Delhi",
            "expected_harvest_date": datetime.now() + timedelta(days=35),
            "price_per_unit": 25.0,
        }

        vector_similarity = 0.90

        match_scores = self.matching_service._calculate_match_score(
            supply_request, listing, vector_similarity
        )

        assert match_scores["distance_km"] is not None
        assert match_scores["distance_km"] < 50  # Within 50 km
        assert match_scores["component_scores"]["location_proximity"] >= 90

        print(f"✓ GPS-based match score: {match_scores['overall_score']:.2f}")
        print(f"  Distance: {match_scores['distance_km']:.2f} km")

    def test_match_reasoning_generation(self):
        """Test generation of human-readable match reasoning"""
        supply_request = {
            "crop_type": "wheat",
            "quality_requirements": "Grade A",
            "quantity_needed": 5000,
            "delivery_state": "Punjab",
            "delivery_district": "Ludhiana",
        }

        listing = {
            "id": 1,
            "farmer_id": 123,
            "crop_type": "wheat",
            "quality_grade": "A",
            "estimated_quantity": 6000,
            "available_quantity": 6000,
            "location_state": "Punjab",
            "location_district": "Ludhiana",
        }

        match_scores = {
            "overall_score": 92.5,
            "component_scores": {
                "crop_match": 95,
                "quality_match": 100,
                "quantity_match": 100,
                "location_proximity": 100,
                "timing_alignment": 90,
            },
            "distance_km": None,
        }

        reasoning = self.matching_service._generate_match_reasoning(
            supply_request, listing, match_scores
        )

        assert reasoning is not None
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
        assert "crop match" in reasoning.lower() or "quality" in reasoning.lower()

        print(f"✓ Match reasoning generated: {reasoning}")

    def test_weighted_score_calculation(self):
        """Test that weighted scores sum correctly"""
        # Verify weights sum to 100
        total_weight = sum(self.matching_service.weights.values())
        assert total_weight == 100

        # Test with all perfect scores
        component_scores = {
            "crop_match": 100,
            "quality_match": 100,
            "quantity_match": 100,
            "location_proximity": 100,
            "timing_alignment": 100,
        }

        overall = (
            component_scores["crop_match"] * self.matching_service.weights["crop_match"] / 100
            + component_scores["quality_match"]
            * self.matching_service.weights["quality_match"]
            / 100
            + component_scores["quantity_match"]
            * self.matching_service.weights["quantity_match"]
            / 100
            + component_scores["location_proximity"]
            * self.matching_service.weights["location_proximity"]
            / 100
            + component_scores["timing_alignment"]
            * self.matching_service.weights["timing_alignment"]
            / 100
        )

        assert overall == 100.0
        print(f"✓ Weighted score calculation verified: {overall}")

    def test_aggregated_options_creation(self):
        """Test creation of multi-farmer aggregation options"""
        supply_request = {
            "crop_type": "wheat",
            "quantity_needed": 10000,
            "delivery_state": "Punjab",
            "delivery_district": "Ludhiana",
        }

        candidates = [
            {
                "listing_id": 1,
                "farmer_id": 101,
                "matched_quantity": 3000,
                "price_offered": 25.0,
                "match_score": 85,
                "component_scores": {"location_proximity": 100},
            },
            {
                "listing_id": 2,
                "farmer_id": 102,
                "matched_quantity": 4000,
                "price_offered": 24.5,
                "match_score": 82,
                "component_scores": {"location_proximity": 100},
            },
            {
                "listing_id": 3,
                "farmer_id": 103,
                "matched_quantity": 3500,
                "price_offered": 26.0,
                "match_score": 80,
                "component_scores": {"location_proximity": 100},
            },
        ]

        aggregated_options = self.matching_service._create_aggregated_options(
            supply_request, candidates, 10000
        )

        assert len(aggregated_options) > 0
        assert aggregated_options[0]["total_quantity"] >= 8000  # At least 80% fulfillment
        assert len(aggregated_options[0]["farmers"]) >= 2
        assert "average_price" in aggregated_options[0]
        assert "match_score" in aggregated_options[0]

        print(f"✓ Aggregated options created: {len(aggregated_options)} options")
        print(
            f"  Option 1: {len(aggregated_options[0]['farmers'])} farmers, {aggregated_options[0]['total_quantity']}kg"
        )

    def test_recommendation_generation(self):
        """Test overall recommendation generation"""
        # Test with excellent single match
        single_matches = [{"farmer_id": 101, "match_score": 92.5}]
        aggregated_options = []

        recommendation = self.matching_service._generate_recommendation(
            single_matches, aggregated_options
        )

        assert "excellent" in recommendation.lower() or "found" in recommendation.lower()
        print(f"✓ Recommendation (excellent match): {recommendation}")

        # Test with no matches
        recommendation = self.matching_service._generate_recommendation([], [])
        assert "no" in recommendation.lower()
        print(f"✓ Recommendation (no matches): {recommendation}")

        # Test with aggregated options only
        aggregated_options = [
            {"farmers": [{"farmer_id": 101}, {"farmer_id": 102}], "match_score": 75}
        ]
        recommendation = self.matching_service._generate_recommendation([], aggregated_options)
        assert "multi-farmer" in recommendation.lower() or "coordination" in recommendation.lower()
        print(f"✓ Recommendation (aggregated): {recommendation}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
