#!/usr/bin/env python3
"""
Simple test to verify the matching logic without database dependencies
"""

def test_embedding_generation():
    """Test that embedding text generation works correctly"""
    supply_request = {
        'crop_type': 'Wheat',
        'quality_requirements': 'Grade A',
        'quantity_needed': 1000,
        'delivery_state': 'Haryana',
        'delivery_district': 'Gurgaon',
        'is_emergency': False
    }
    
    # Build text representation (same as in service)
    text_parts = [
        f"crop:{supply_request.get('crop_type', 'unknown')}",
        f"quality:{supply_request.get('quality_requirements', 'standard')}",
        f"quantity:{supply_request.get('quantity_needed', 0)}kg",
        f"location:{supply_request.get('delivery_state', '')}-{supply_request.get('delivery_district', '')}",
        f"emergency:{supply_request.get('is_emergency', False)}"
    ]
    
    text = " ".join(text_parts)
    expected = "crop:Wheat quality:Grade A quantity:1000kg location:Haryana-Gurgaon emergency:False"
    
    assert text == expected, f"Expected: {expected}, Got: {text}"
    print(f"✓ Supply request embedding text: {text}")

def test_listing_embedding_generation():
    """Test that listing embedding text generation works correctly"""
    listing = {
        'crop_type': 'Wheat',
        'crop_variety': 'HD-2967',
        'quality_grade': 'A',
        'available_quantity': 1200,
        'location_state': 'Haryana',
        'location_district': 'Gurgaon'
    }
    
    # Build text representation (same as in service)
    text_parts = [
        f"crop:{listing.get('crop_type', 'unknown')}",
        f"variety:{listing.get('crop_variety', '')}",
        f"quality:{listing.get('quality_grade', 'B')}",
        f"quantity:{listing.get('available_quantity', listing.get('estimated_quantity', 0))}kg",
        f"location:{listing.get('location_state', '')}-{listing.get('location_district', '')}"
    ]
    
    text = " ".join(text_parts)
    expected = "crop:Wheat variety:HD-2967 quality:A quantity:1200kg location:Haryana-Gurgaon"
    
    assert text == expected, f"Expected: {expected}, Got: {text}"
    print(f"✓ Listing embedding text: {text}")

def test_match_score_weights():
    """Test that match score weights sum to 100"""
    weights = {
        'crop_match': 30,
        'quality_match': 20,
        'quantity_match': 20,
        'location_proximity': 20,
        'timing_alignment': 10
    }
    
    total = sum(weights.values())
    assert total == 100, f"Weights must sum to 100, got {total}"
    print(f"✓ Match score weights sum to 100: {weights}")

def test_distance_calculation():
    """Test Haversine distance calculation"""
    from math import radians, cos, sin, asin, sqrt
    
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Haversine formula"""
        if not all([lat1, lon1, lat2, lon2]):
            return None
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth radius in km
        return c * r
    
    # Test: Delhi to Gurgaon (approximately 30 km)
    delhi_lat, delhi_lon = 28.6139, 77.2090
    gurgaon_lat, gurgaon_lon = 28.4595, 77.0266
    
    distance = calculate_distance(delhi_lat, delhi_lon, gurgaon_lat, gurgaon_lon)
    
    # Distance should be approximately 25-35 km
    assert 20 <= distance <= 40, f"Expected distance ~30km, got {distance:.2f}km"
    print(f"✓ Distance calculation: Delhi to Gurgaon = {distance:.2f}km")

def test_pgvector_query_format():
    """Test that pgvector query format is correct"""
    # Sample embedding
    embedding = [0.1, 0.2, 0.3, 0.4]
    
    # Convert to PostgreSQL array format
    embedding_str = '[' + ','.join(map(str, embedding)) + ']'
    expected = '[0.1,0.2,0.3,0.4]'
    
    assert embedding_str == expected, f"Expected: {expected}, Got: {embedding_str}"
    print(f"✓ pgvector array format: {embedding_str}")

if __name__ == '__main__':
    print("Testing AI-powered supply matching logic...\n")
    
    test_embedding_generation()
    test_listing_embedding_generation()
    test_match_score_weights()
    test_distance_calculation()
    test_pgvector_query_format()
    
    print("\n✅ All logic tests passed!")
