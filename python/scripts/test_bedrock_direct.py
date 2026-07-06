import asyncio
import os
import sys

# Add the project directory to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.bedrock_service import BedrockService
from app.core.database import SessionLocal

async def test_bedrock():
    try:
        print("Initializing BedrockService...")
        svc = BedrockService()
        
        print("Calling get_annual_crop_strategy...")
        result = await svc.get_annual_crop_strategy(
            state="Haryana",
            district="Gurgaon",
            soil_type="loamy",
            area_acres=5.5,
            irrigation_type="drip"
        )
        print("Success!")
        print(result)
    except Exception as e:
        import traceback
        print(f"FAILED WITH EXCEPTION: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bedrock())
