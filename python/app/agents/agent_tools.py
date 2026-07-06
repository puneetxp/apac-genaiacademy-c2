"""
Shared tools for Google Antigravity AI agents in CropSense.
These tools allow the agents to query the primary PostgreSQL database and the OpenWeather/IMD APIs.
"""

import logging
from typing import Dict, Any, List, Optional
from app.core.database import get_db_context
from app.orm.farm import Farm
from app.orm.farm_plot import FarmPlot
from app.orm.soil_test_result import SoilTestResult
from app.orm.market_price import MarketPrice
from app.services.weather_service import WeatherService

logger = logging.getLogger(__name__)

def get_farm_details(farm_id: int) -> str:
    """Retrieves metadata for a specific farm (owner user ID, size in acres, location details).

    Args:
        farm_id: The unique ID of the farm.
    """
    try:
        with get_db_context() as db:
            farm = db.query(Farm).filter(Farm.id == farm_id).first()
            if not farm:
                return f"Farm with ID {farm_id} not found."
            
            return (
                f"Farm ID: {farm.id}\n"
                f"User ID: {farm.user_id}\n"
                f"State: {farm.state}\n"
                f"District: {farm.district}\n"
                f"Pincode: {farm.pincode}\n"
                f"Latitude: {farm.latitude}\n"
                f"Longitude: {farm.longitude}\n"
                f"Total Area: {farm.total_area_acres} acres\n"
                f"Soil Type: {farm.primary_soil_type}\n"
                f"Irrigation: {farm.irrigation_source}\n"
            )
    except Exception as e:
        logger.error(f"Error getting farm details: {e}")
        return f"Error retrieving details for farm {farm_id}: {str(e)}"

def get_soil_info(plot_id: int) -> str:
    """Retrieves the latest soil test results for a specific farm plot.

    Args:
        plot_id: The unique ID of the farm plot.
    """
    try:
        with get_db_context() as db:
            plot = db.query(FarmPlot).filter(FarmPlot.id == plot_id).first()
            if not plot:
                return f"Farm plot with ID {plot_id} not found."
            
            soil_test = db.query(SoilTestResult).filter(
                SoilTestResult.farm_plot_id == plot_id
            ).order_by(SoilTestResult.tested_at.desc()).first()
            
            plot_info = f"Plot ID: {plot.id}, Size: {plot.area_acres} acres, Soil Type: {plot.soil_type}\n"
            if not soil_test:
                return plot_info + "No soil test records found for this plot."
            
            return (
                plot_info +
                f"Soil Test Date: {soil_test.tested_at}\n"
                f"Nitrogen (N): {soil_test.nitrogen_content} kg/ha\n"
                f"Phosphorus (P): {soil_test.phosphorus_content} kg/ha\n"
                f"Potassium (K): {soil_test.potassium_content} kg/ha\n"
                f"pH level: {soil_test.ph_level}\n"
                f"Organic Carbon: {soil_test.organic_carbon_content}%\n"
                f"Electrical Conductivity: {soil_test.electrical_conductivity} dS/m\n"
                f"Recommendation: {soil_test.fertilizer_recommendation or 'None'}"
            )
    except Exception as e:
        logger.error(f"Error getting soil info: {e}")
        return f"Error retrieving soil info for plot {plot_id}: {str(e)}"

async def get_weather_forecast(latitude: float, longitude: float) -> str:
    """Fetches weather forecast details for agricultural coordinates.

    Args:
        latitude: GPS latitude of the location.
        longitude: GPS longitude of the location.
    """
    try:
        # Use database context to create weather service
        with get_db_context() as db:
            weather_service = WeatherService(db)
            forecast = await weather_service.get_forecast(latitude, longitude)
            if not forecast:
                return "Failed to fetch weather forecast data."
            
            # Formulate summary
            summary = []
            for day in forecast[:5]:  # Return 5-day forecast
                summary.append(
                    f"Date: {day.get('date')}, Temp: {day.get('min_temp')}°C to {day.get('max_temp')}°C, "
                    f"Rainfall: {day.get('rainfall')}mm, Condition: {day.get('condition')}"
                )
            return "\n".join(summary)
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        return f"Error retrieving weather forecast: {str(e)}"

def get_market_prices(crop_name: str) -> str:
    """Retrieves current market prices and historical price trends for a crop.

    Args:
        crop_name: The name of the crop (e.g. "Rice", "Wheat").
    """
    try:
        with get_db_context() as db:
            prices = db.query(MarketPrice).filter(
                MarketPrice.crop_name.ilike(f"%{crop_name}%")
            ).order_by(MarketPrice.updated_at.desc()).limit(5).all()
            
            if not prices:
                return f"No price listings found for crop '{crop_name}'."
            
            summary = []
            for price in prices:
                summary.append(
                    f"Market: {price.market_name}, State: {price.state}, District: {price.district}, "
                    f"Price: Rs.{price.min_price} to Rs.{price.max_price} per quintal, Date: {price.updated_at.strftime('%Y-%m-%d')}"
                )
            return "\n".join(summary)
    except Exception as e:
        logger.error(f"Error getting market prices: {e}")
        return f"Error retrieving market prices: {str(e)}"
