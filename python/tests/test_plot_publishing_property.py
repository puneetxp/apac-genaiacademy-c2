"""
Property-based tests for plot publishing completeness
Tests Property 21: Plot Publishing Completeness

**Validates: Requirements AC7 (Smart Land Plot Management)**
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from hypothesis import given, strategies as st, settings, HealthCheck
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime, date, timedelta

from app.services.plot_publishing_service import PlotPublishingService
from app.orm.farm_plot import FarmPlot
from app.orm.user import User


# Custom strategies for generating valid plot publishing data
@st.composite
def plot_publishing_data_strategy(draw):
    """
    Generate valid plot publishing data
    
    This strategy creates plots with all required information for publishing
    to the marketplace.
    """
    
    # Indian states and districts
    states = [
        "Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan",
        "Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh", "Gujarat"
    ]
    
    districts = [
        "Ludhiana", "Amritsar", "Patiala", "Jalandhar", "Bathinda",
        "Karnal", "Hisar", "Panipat", "Agra", "Lucknow"
    ]
    
    soil_types = ["clay", "sandy", "loamy", "black", "red"]
    irrigation_types = ["Canal", "Borewell", "Rain-fed", "Mixed"]
    crops = ["Rice", "Wheat", "Cotton", "Maize", "Soybean", "Sugarcane"]
    varieties = ["Basmati 1121", "HD-2967", "BT Cotton", "Hybrid Maize", "JS 335"]
    quality_grades = ["A", "B", "C"]
    
    # Generate plot data
    plot_id = draw(st.integers(min_value=1, max_value=10000))
    plot_name = draw(st.text(min_size=5, max_size=30, alphabet=st.characters(min_codepoint=65, max_codepoint=122)))
    area = draw(st.floats(min_value=0.5, max_value=100.0))
    soil_type = draw(st.sampled_from(soil_types))
    irrigation_type = draw(st.sampled_from(irrigation_types))
    state = draw(st.sampled_from(states))
    district = draw(st.sampled_from(districts))
    farm_id = draw(st.integers(min_value=1, max_value=1000))
    
    # Generate crop publishing data
    crop_name = draw(st.sampled_from(crops))
    crop_variety = draw(st.sampled_from(varieties))
    
    # Generate harvest date (30-180 days in future)
    days_ahead = draw(st.integers(min_value=30, max_value=180))
    harvest_date = date.today() + timedelta(days=days_ahead)
    
    quantity_quintals = draw(st.floats(min_value=5.0, max_value=200.0))
    quality_grade = draw(st.sampled_from(quality_grades))
    price_per_quintal = draw(st.floats(min_value=1000.0, max_value=10000.0))
    
    # Create mock plot object
    plot = Mock(spec=FarmPlot)
    plot.id = plot_id
    plot.plot_name = plot_name
    plot.area = Decimal(str(area))
    plot.soil_type = soil_type
    plot.irrigation_type = irrigation_type
    plot.state = state
    plot.district = district
    plot.farm_id = farm_id
    plot.investment_capacity = Decimal("20000")
    
    # Create mock farmer object
    farmer_id = draw(st.integers(min_value=1, max_value=10000))
    farmer = Mock(spec=User)
    farmer.id = farmer_id
    farmer.email = f"farmer{farmer_id}@example.com"
    farmer.phone_number = f"+91{draw(st.integers(min_value=7000000000, max_value=9999999999))}"
    
    return {
        "plot": plot,
        "farmer": farmer,
        "crop_name": crop_name,
        "crop_variety": crop_variety,
        "expected_harvest_date": harvest_date.isoformat(),
        "quantity_quintals": quantity_quintals,
        "quality_grade": quality_grade,
        "price_per_quintal": price_per_quintal
    }


@st.composite
def ai_predictions_strategy(draw):
    """Generate AI predictions for published plots"""
    
    # Generate harvest date range
    days_ahead = draw(st.integers(min_value=30, max_value=180))
    harvest_date = date.today() + timedelta(days=days_ahead)
    harvest_start = harvest_date - timedelta(days=7)
    harvest_end = harvest_date + timedelta(days=7)
    
    return {
        "yield_confidence": draw(st.floats(min_value=0.5, max_value=1.0)),
        "quality_confidence": draw(st.floats(min_value=0.5, max_value=1.0)),
        "harvest_date_range": {
            "start": harvest_start.isoformat(),
            "end": harvest_end.isoformat()
        },
        "ai_analysis_available": draw(st.booleans()),
        "suitability_score": draw(st.floats(min_value=5.0, max_value=10.0)),
        "risk_level": draw(st.sampled_from(["low", "medium", "high"]))
    }


class TestPlotPublishingCompleteness:
    """
    Property 21: Plot Publishing Completeness
    
    Test that for any published plot, marketplace listing contains all
    required information: plot details, crop details, AI predictions,
    offering terms. Validate listing is searchable and visible to buyers.
    """
    
    @given(
        publishing_data=plot_publishing_data_strategy(),
        ai_predictions=ai_predictions_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,  # 15 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_published_plot_contains_all_required_fields(
        self,
        publishing_data,
        ai_predictions
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any published plot, marketplace listing contains
        all required information without missing fields.
        """
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotPublishingService(mock_db)
        
        # Mock the internal methods
        with patch.object(service, '_get_plot', return_value=publishing_data['plot']), \
             patch.object(service, '_get_farmer', return_value=publishing_data['farmer']), \
             patch.object(service, '_generate_ai_predictions', return_value=ai_predictions), \
             patch.object(service.db, 'add'), \
             patch.object(service.db, 'commit'), \
             patch.object(service.db, 'refresh'):
            
            # Execute
            result = await service.publish_plot(
                plot_id=publishing_data['plot'].id,
                crop_name=publishing_data['crop_name'],
                crop_variety=publishing_data['crop_variety'],
                expected_harvest_date=publishing_data['expected_harvest_date'],
                quantity_quintals=publishing_data['quantity_quintals'],
                quality_grade=publishing_data['quality_grade'],
                price_per_quintal=publishing_data['price_per_quintal'],
                farmer_id=publishing_data['farmer'].id
            )
            
            # Assert: Basic response structure
            assert result is not None, "Published listing cannot be None"
            assert "listing_id" in result, "listing_id missing from response"
            assert "plot_id" in result, "plot_id missing from response"
            assert "plot_name" in result, "plot_name missing from response"
            assert "status" in result, "status missing from response"
            assert result["status"] == "published", "Status must be 'published'"
            
            # Assert: Crop details section
            assert "crop_details" in result, "crop_details missing from response"
            crop_details = result["crop_details"]
            
            assert "crop_name" in crop_details, "crop_name missing from crop_details"
            assert crop_details["crop_name"] == publishing_data['crop_name'], \
                "crop_name mismatch"
            
            assert "crop_variety" in crop_details, "crop_variety missing from crop_details"
            assert crop_details["crop_variety"] == publishing_data['crop_variety'], \
                "crop_variety mismatch"
            
            assert "expected_harvest_date" in crop_details, \
                "expected_harvest_date missing from crop_details"
            
            assert "quantity_quintals" in crop_details, \
                "quantity_quintals missing from crop_details"
            assert crop_details["quantity_quintals"] == publishing_data['quantity_quintals'], \
                "quantity_quintals mismatch"
            
            assert "quantity_kg" in crop_details, \
                "quantity_kg missing from crop_details"
            
            assert "quality_grade" in crop_details, \
                "quality_grade missing from crop_details"
            assert crop_details["quality_grade"] in ["A", "B", "C"], \
                f"Invalid quality_grade: {crop_details['quality_grade']}"
            
            assert "price_per_quintal" in crop_details, \
                "price_per_quintal missing from crop_details"

    
    @given(
        publishing_data=plot_publishing_data_strategy(),
        ai_predictions=ai_predictions_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_plot_characteristics_completeness(
        self,
        publishing_data,
        ai_predictions
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any published plot, plot characteristics section
        contains complete location, area, soil, and irrigation information.
        """
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotPublishingService(mock_db)
        
        # Mock the internal methods
        with patch.object(service, '_get_plot', return_value=publishing_data['plot']), \
             patch.object(service, '_get_farmer', return_value=publishing_data['farmer']), \
             patch.object(service, '_generate_ai_predictions', return_value=ai_predictions), \
             patch.object(service.db, 'add'), \
             patch.object(service.db, 'commit'), \
             patch.object(service.db, 'refresh'):
            
            # Execute
            result = await service.publish_plot(
                plot_id=publishing_data['plot'].id,
                crop_name=publishing_data['crop_name'],
                crop_variety=publishing_data['crop_variety'],
                expected_harvest_date=publishing_data['expected_harvest_date'],
                quantity_quintals=publishing_data['quantity_quintals'],
                quality_grade=publishing_data['quality_grade'],
                price_per_quintal=publishing_data['price_per_quintal'],
                farmer_id=publishing_data['farmer'].id
            )
            
            # Assert: Plot characteristics section
            assert "plot_characteristics" in result, \
                "plot_characteristics missing from response"
            plot_chars = result["plot_characteristics"]
            
            # Location information
            assert "location" in plot_chars, "location missing from plot_characteristics"
            location = plot_chars["location"]
            
            assert "state" in location, "state missing from location"
            assert location["state"] == publishing_data['plot'].state, "state mismatch"
            
            assert "district" in location, "district missing from location"
            assert location["district"] == publishing_data['plot'].district, "district mismatch"
            
            # Area information
            assert "area_acres" in plot_chars, "area_acres missing from plot_characteristics"
            assert isinstance(plot_chars["area_acres"], (int, float)), \
                "area_acres must be numeric"
            assert plot_chars["area_acres"] > 0, "area_acres must be positive"
            
            # Soil type
            assert "soil_type" in plot_chars, "soil_type missing from plot_characteristics"
            assert plot_chars["soil_type"] == publishing_data['plot'].soil_type, \
                "soil_type mismatch"
            
            # Irrigation type
            assert "irrigation_type" in plot_chars, \
                "irrigation_type missing from plot_characteristics"
            assert plot_chars["irrigation_type"] == publishing_data['plot'].irrigation_type, \
                "irrigation_type mismatch"

    
    @given(
        publishing_data=plot_publishing_data_strategy(),
        ai_predictions=ai_predictions_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_ai_predictions_completeness(
        self,
        publishing_data,
        ai_predictions
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any published plot, AI predictions section contains
        yield confidence, quality confidence, and harvest date range.
        """
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotPublishingService(mock_db)
        
        # Mock the internal methods
        with patch.object(service, '_get_plot', return_value=publishing_data['plot']), \
             patch.object(service, '_get_farmer', return_value=publishing_data['farmer']), \
             patch.object(service, '_generate_ai_predictions', return_value=ai_predictions), \
             patch.object(service.db, 'add'), \
             patch.object(service.db, 'commit'), \
             patch.object(service.db, 'refresh'):
            
            # Execute
            result = await service.publish_plot(
                plot_id=publishing_data['plot'].id,
                crop_name=publishing_data['crop_name'],
                crop_variety=publishing_data['crop_variety'],
                expected_harvest_date=publishing_data['expected_harvest_date'],
                quantity_quintals=publishing_data['quantity_quintals'],
                quality_grade=publishing_data['quality_grade'],
                price_per_quintal=publishing_data['price_per_quintal'],
                farmer_id=publishing_data['farmer'].id
            )
            
            # Assert: AI predictions section
            assert "ai_predictions" in result, "ai_predictions missing from response"
            ai_pred = result["ai_predictions"]
            
            # Yield confidence
            assert "yield_confidence" in ai_pred, \
                "yield_confidence missing from ai_predictions"
            assert isinstance(ai_pred["yield_confidence"], (int, float)), \
                "yield_confidence must be numeric"
            assert 0.0 <= ai_pred["yield_confidence"] <= 1.0, \
                f"yield_confidence {ai_pred['yield_confidence']} out of range [0, 1]"
            
            # Quality confidence
            assert "quality_confidence" in ai_pred, \
                "quality_confidence missing from ai_predictions"
            assert isinstance(ai_pred["quality_confidence"], (int, float)), \
                "quality_confidence must be numeric"
            assert 0.0 <= ai_pred["quality_confidence"] <= 1.0, \
                f"quality_confidence {ai_pred['quality_confidence']} out of range [0, 1]"
            
            # Harvest date range
            assert "harvest_date_range" in ai_pred, \
                "harvest_date_range missing from ai_predictions"
            date_range = ai_pred["harvest_date_range"]
            
            assert "start" in date_range, "start missing from harvest_date_range"
            assert "end" in date_range, "end missing from harvest_date_range"
            
            # Validate date format
            try:
                start_date = date.fromisoformat(date_range["start"])
                end_date = date.fromisoformat(date_range["end"])
                assert start_date < end_date, "start date must be before end date"
            except ValueError:
                pytest.fail("Invalid date format in harvest_date_range")
            
            # Suitability score
            assert "suitability_score" in ai_pred, \
                "suitability_score missing from ai_predictions"
            assert isinstance(ai_pred["suitability_score"], (int, float)), \
                "suitability_score must be numeric"
            assert 0.0 <= ai_pred["suitability_score"] <= 10.0, \
                f"suitability_score {ai_pred['suitability_score']} out of range [0, 10]"
            
            # Risk level
            assert "risk_level" in ai_pred, "risk_level missing from ai_predictions"
            assert ai_pred["risk_level"] in ["low", "medium", "high"], \
                f"Invalid risk_level: {ai_pred['risk_level']}"

    
    @given(
        publishing_data=plot_publishing_data_strategy(),
        ai_predictions=ai_predictions_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_offering_terms_completeness(
        self,
        publishing_data,
        ai_predictions
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any published plot, offering terms section contains
        pricing, total value, and advance booking information.
        """
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotPublishingService(mock_db)
        
        # Mock the internal methods
        with patch.object(service, '_get_plot', return_value=publishing_data['plot']), \
             patch.object(service, '_get_farmer', return_value=publishing_data['farmer']), \
             patch.object(service, '_generate_ai_predictions', return_value=ai_predictions), \
             patch.object(service.db, 'add'), \
             patch.object(service.db, 'commit'), \
             patch.object(service.db, 'refresh'):
            
            # Execute
            result = await service.publish_plot(
                plot_id=publishing_data['plot'].id,
                crop_name=publishing_data['crop_name'],
                crop_variety=publishing_data['crop_variety'],
                expected_harvest_date=publishing_data['expected_harvest_date'],
                quantity_quintals=publishing_data['quantity_quintals'],
                quality_grade=publishing_data['quality_grade'],
                price_per_quintal=publishing_data['price_per_quintal'],
                farmer_id=publishing_data['farmer'].id
            )
            
            # Assert: Offering terms section
            assert "offering_terms" in result, "offering_terms missing from response"
            terms = result["offering_terms"]
            
            # Price per quintal
            assert "price_per_quintal" in terms, \
                "price_per_quintal missing from offering_terms"
            assert isinstance(terms["price_per_quintal"], (int, float)), \
                "price_per_quintal must be numeric"
            assert terms["price_per_quintal"] > 0, \
                "price_per_quintal must be positive"
            assert terms["price_per_quintal"] == publishing_data['price_per_quintal'], \
                "price_per_quintal mismatch"
            
            # Total value
            assert "total_value" in terms, "total_value missing from offering_terms"
            assert isinstance(terms["total_value"], (int, float)), \
                "total_value must be numeric"
            assert terms["total_value"] > 0, "total_value must be positive"
            
            # Verify total value calculation
            expected_total = publishing_data['price_per_quintal'] * publishing_data['quantity_quintals']
            assert abs(terms["total_value"] - expected_total) < 1.0, \
                f"total_value calculation incorrect. Expected {expected_total}, got {terms['total_value']}"
            
            # Advance booking availability
            assert "advance_booking_available" in terms, \
                "advance_booking_available missing from offering_terms"
            assert isinstance(terms["advance_booking_available"], bool), \
                "advance_booking_available must be boolean"
            
            # Minimum booking quantity
            assert "minimum_booking_quantity" in terms, \
                "minimum_booking_quantity missing from offering_terms"
            assert isinstance(terms["minimum_booking_quantity"], (int, float)), \
                "minimum_booking_quantity must be numeric"
            assert terms["minimum_booking_quantity"] > 0, \
                "minimum_booking_quantity must be positive"
            assert terms["minimum_booking_quantity"] <= publishing_data['quantity_quintals'], \
                "minimum_booking_quantity cannot exceed total quantity"

    
    @given(
        publishing_data=plot_publishing_data_strategy(),
        ai_predictions=ai_predictions_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_farmer_contact_information_present(
        self,
        publishing_data,
        ai_predictions
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any published plot, farmer contact information
        is present for buyer communication.
        """
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotPublishingService(mock_db)
        
        # Mock the internal methods
        with patch.object(service, '_get_plot', return_value=publishing_data['plot']), \
             patch.object(service, '_get_farmer', return_value=publishing_data['farmer']), \
             patch.object(service, '_generate_ai_predictions', return_value=ai_predictions), \
             patch.object(service.db, 'add'), \
             patch.object(service.db, 'commit'), \
             patch.object(service.db, 'refresh'):
            
            # Execute
            result = await service.publish_plot(
                plot_id=publishing_data['plot'].id,
                crop_name=publishing_data['crop_name'],
                crop_variety=publishing_data['crop_variety'],
                expected_harvest_date=publishing_data['expected_harvest_date'],
                quantity_quintals=publishing_data['quantity_quintals'],
                quality_grade=publishing_data['quality_grade'],
                price_per_quintal=publishing_data['price_per_quintal'],
                farmer_id=publishing_data['farmer'].id
            )
            
            # Assert: Farmer contact section
            assert "farmer_contact" in result, "farmer_contact missing from response"
            contact = result["farmer_contact"]
            
            # Phone number
            assert "phone" in contact, "phone missing from farmer_contact"
            # Phone can be None if not provided, but field must exist
            
            # Email
            assert "email" in contact, "email missing from farmer_contact"
            # Email can be None if not provided, but field must exist

    
    @given(
        publishing_data=plot_publishing_data_strategy(),
        ai_predictions=ai_predictions_strategy()
    )
    @settings(
        max_examples=50,  # Fewer examples for integration test
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_listing_searchability_and_visibility(
        self,
        publishing_data,
        ai_predictions
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any published plot, listing is searchable and
        visible to buyers with status "published".
        """
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotPublishingService(mock_db)
        
        # Mock the internal methods
        with patch.object(service, '_get_plot', return_value=publishing_data['plot']), \
             patch.object(service, '_get_farmer', return_value=publishing_data['farmer']), \
             patch.object(service, '_generate_ai_predictions', return_value=ai_predictions), \
             patch.object(service.db, 'add'), \
             patch.object(service.db, 'commit'), \
             patch.object(service.db, 'refresh'):
            
            # Execute
            result = await service.publish_plot(
                plot_id=publishing_data['plot'].id,
                crop_name=publishing_data['crop_name'],
                crop_variety=publishing_data['crop_variety'],
                expected_harvest_date=publishing_data['expected_harvest_date'],
                quantity_quintals=publishing_data['quantity_quintals'],
                quality_grade=publishing_data['quality_grade'],
                price_per_quintal=publishing_data['price_per_quintal'],
                farmer_id=publishing_data['farmer'].id
            )
            
            # Assert: Listing is published and visible
            assert result["status"] == "published", \
                "Listing status must be 'published' for buyer visibility"
            
            # Assert: All searchable fields are present
            # Buyers should be able to search by:
            # - Crop type
            assert "crop_details" in result, "crop_details required for search"
            assert "crop_name" in result["crop_details"], \
                "crop_name required for crop type search"
            
            # - Location (state, district)
            assert "plot_characteristics" in result, \
                "plot_characteristics required for location search"
            assert "location" in result["plot_characteristics"], \
                "location required for geographic search"
            assert "state" in result["plot_characteristics"]["location"], \
                "state required for location search"
            assert "district" in result["plot_characteristics"]["location"], \
                "district required for location search"
            
            # - Harvest date
            assert "expected_harvest_date" in result["crop_details"], \
                "expected_harvest_date required for harvest timing search"
            
            # - Quality grade
            assert "quality_grade" in result["crop_details"], \
                "quality_grade required for quality filtering"
            
            # - Quantity
            assert "quantity_quintals" in result["crop_details"], \
                "quantity_quintals required for quantity filtering"
            
            # Assert: Listing has unique identifier
            assert "listing_id" in result, "listing_id required for buyer access"
            assert result["listing_id"] is not None, "listing_id cannot be None"

    
    @given(
        publishing_data=plot_publishing_data_strategy(),
        ai_predictions=ai_predictions_strategy()
    )
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    @pytest.mark.asyncio
    async def test_quantity_conversion_accuracy(
        self,
        publishing_data,
        ai_predictions
    ):
        """
        **Validates: Requirements AC7 (Smart Land Plot Management)**
        
        Property: For any published plot, quantity conversion from
        quintals to kg is mathematically accurate (1 quintal = 100 kg).
        """
        
        # Setup mock database and service
        mock_db = AsyncMock()
        service = PlotPublishingService(mock_db)
        
        # Mock the internal methods
        with patch.object(service, '_get_plot', return_value=publishing_data['plot']), \
             patch.object(service, '_get_farmer', return_value=publishing_data['farmer']), \
             patch.object(service, '_generate_ai_predictions', return_value=ai_predictions), \
             patch.object(service.db, 'add'), \
             patch.object(service.db, 'commit'), \
             patch.object(service.db, 'refresh'):
            
            # Execute
            result = await service.publish_plot(
                plot_id=publishing_data['plot'].id,
                crop_name=publishing_data['crop_name'],
                crop_variety=publishing_data['crop_variety'],
                expected_harvest_date=publishing_data['expected_harvest_date'],
                quantity_quintals=publishing_data['quantity_quintals'],
                quality_grade=publishing_data['quality_grade'],
                price_per_quintal=publishing_data['price_per_quintal'],
                farmer_id=publishing_data['farmer'].id
            )
            
            # Assert: Quantity conversion
            crop_details = result["crop_details"]
            
            quantity_quintals = crop_details["quantity_quintals"]
            quantity_kg = crop_details["quantity_kg"]
            
            # Verify conversion: 1 quintal = 100 kg
            expected_kg = int(quantity_quintals * 100)
            assert quantity_kg == expected_kg, \
                f"Quantity conversion incorrect. Expected {expected_kg} kg, got {quantity_kg} kg"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
