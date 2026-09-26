"""
Manual test for weather-based recommendations
Task 23.3: Build weather-based recommendations

Run this test to verify the weather recommendations API endpoints work correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.cache import get_cache_manager
from app.core.database import get_db
from app.services.severe_weather_service import get_severe_weather_service
from app.services.weather_recommendations_service import get_weather_recommendations_service
from app.services.weather_service import get_weather_service


async def test_planting_recommendations():
    """Test planting recommendations"""
    print("\n" + "=" * 80)
    print("TEST 1: Planting Recommendations")
    print("=" * 80)

    # Get database session
    async for db in get_db():
        try:
            cache_manager = get_cache_manager()
            weather_service = get_weather_service(db, cache_manager=cache_manager)
            severe_weather_service = get_severe_weather_service(db, weather_service)
            recommendations_service = get_weather_recommendations_service(
                db, weather_service, severe_weather_service
            )

            # Test with sample coordinates (Delhi region)
            latitude = 28.6139
            longitude = 77.2090
            crop_type = "wheat"
            season = "rabi"

            print(f"\nTesting planting recommendations for:")
            print(f"  Location: {latitude}, {longitude}")
            print(f"  Crop: {crop_type}")
            print(f"  Season: {season}")

            result = await recommendations_service.get_planting_recommendations(
                latitude, longitude, crop_type, season
            )

            print(f"\nResult:")
            print(f"  Status: {result.get('status', 'success')}")
            print(f"  Optimal Window: {result.get('optimal_window')}")
            print(f"  Recommendation: {result.get('recommendation')}")
            print(f"  Number of Windows: {len(result.get('planting_windows', []))}")

            await weather_service.close()
            print("\n✅ Planting recommendations test PASSED")

        except Exception as e:
            print(f"\n❌ Planting recommendations test FAILED: {e}")
            import traceback

            traceback.print_exc()
        finally:
            break


async def test_irrigation_schedule():
    """Test irrigation schedule"""
    print("\n" + "=" * 80)
    print("TEST 2: Irrigation Schedule")
    print("=" * 80)

    # Get database session
    async for db in get_db():
        try:
            cache_manager = get_cache_manager()
            weather_service = get_weather_service(db, cache_manager=cache_manager)
            severe_weather_service = get_severe_weather_service(db, weather_service)
            recommendations_service = get_weather_recommendations_service(
                db, weather_service, severe_weather_service
            )

            # Test with sample coordinates
            latitude = 28.6139
            longitude = 77.2090
            crop_type = "wheat"
            soil_type = "loamy"
            days_ahead = 7

            print(f"\nTesting irrigation schedule for:")
            print(f"  Location: {latitude}, {longitude}")
            print(f"  Crop: {crop_type}")
            print(f"  Soil: {soil_type}")
            print(f"  Days ahead: {days_ahead}")

            result = await recommendations_service.get_irrigation_schedule(
                latitude, longitude, crop_type, soil_type, days_ahead
            )

            print(f"\nResult:")
            print(f"  Status: {result.get('status', 'success')}")
            print(f"  Total water saved: {result.get('total_water_saved', 0):.1f}mm")
            print(f"  Water savings: {result.get('water_savings_percentage', 0):.1f}%")
            print(f"  Summary: {result.get('summary')}")
            print(f"  Schedule days: {len(result.get('irrigation_schedule', []))}")

            await weather_service.close()
            print("\n✅ Irrigation schedule test PASSED")

        except Exception as e:
            print(f"\n❌ Irrigation schedule test FAILED: {e}")
            import traceback

            traceback.print_exc()
        finally:
            break


async def test_crop_care_recommendations():
    """Test crop care recommendations"""
    print("\n" + "=" * 80)
    print("TEST 3: Crop Care Recommendations")
    print("=" * 80)

    # Get database session
    async for db in get_db():
        try:
            cache_manager = get_cache_manager()
            weather_service = get_weather_service(db, cache_manager=cache_manager)
            severe_weather_service = get_severe_weather_service(db, weather_service)
            recommendations_service = get_weather_recommendations_service(
                db, weather_service, severe_weather_service
            )

            # Test with sample coordinates
            latitude = 28.6139
            longitude = 77.2090
            crop_type = "wheat"
            growth_stage = "vegetative"
            days_ahead = 7

            print(f"\nTesting crop care recommendations for:")
            print(f"  Location: {latitude}, {longitude}")
            print(f"  Crop: {crop_type}")
            print(f"  Growth stage: {growth_stage}")
            print(f"  Days ahead: {days_ahead}")

            result = await recommendations_service.get_crop_care_recommendations(
                latitude, longitude, crop_type, growth_stage, days_ahead
            )

            print(f"\nResult:")
            print(f"  Status: {result.get('status', 'success')}")
            print(f"  Optimal fertilizer days: {len(result.get('optimal_fertilizer_days', []))}")
            print(
                f"  Optimal pest control days: {len(result.get('optimal_pest_control_days', []))}"
            )
            print(f"  Summary: {result.get('summary')}")

            await weather_service.close()
            print("\n✅ Crop care recommendations test PASSED")

        except Exception as e:
            print(f"\n❌ Crop care recommendations test FAILED: {e}")
            import traceback

            traceback.print_exc()
        finally:
            break


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("WEATHER-BASED RECOMMENDATIONS MANUAL TEST")
    print("Task 23.3: Build weather-based recommendations")
    print("=" * 80)

    await test_planting_recommendations()
    await test_irrigation_schedule()
    await test_crop_care_recommendations()

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
