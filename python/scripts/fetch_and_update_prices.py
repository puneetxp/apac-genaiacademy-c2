"""
Fetch crop market prices from Agmarknet API and update PostgreSQL database.
"""

import sys
import os
import datetime

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.orm.crop_market_data import CropMarketData

def fetch_external_market_prices():
    """
    Simulates fetching real-time market prices from Agmarknet API.
    In production, this makes a request to the Indian Government open API:
    https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=YOUR_API_KEY
    """
    print("Fetching latest crop market prices from Agmarknet API (mocked)...")
    
    # Returns fresh crop prices matching PostgreSQL schema columns
    return [
        {
            "enable": 1,
            "crop_name": "Wheat",
            "state": "Madhya Pradesh",
            "district": "Indore",
            "price_per_kg": 25,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "season": "rabi",
            "yoy_growth": 5,
            "demand_level": "high"
        },
        {
            "enable": 1,
            "crop_name": "Paddy",
            "state": "Haryana",
            "district": "Karnal",
            "price_per_kg": 41,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "season": "kharif",
            "yoy_growth": 7,
            "demand_level": "high"
        },
        {
            "enable": 1,
            "crop_name": "Onion",
            "state": "Maharashtra",
            "district": "Nashik",
            "price_per_kg": 18,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "season": "kharif",
            "yoy_growth": 12,
            "demand_level": "medium"
        }
    ]

def main():
    print("====================================================")
    print("Fetching and Updating Crop Market Prices in PostgreSQL")
    print("====================================================")
    
    # 1. Fetch latest prices
    api_prices = fetch_external_market_prices()
    
    print("\nUpdating PostgreSQL database using Custom ORM...")
    
    success_count = 0
    for price_data in api_prices:
        try:
            # Insert into database
            CropMarketData.create(price_data)
            print(f"✅ Successfully inserted/updated price for {price_data['crop_name']} in {price_data['state']}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to insert price for {price_data['crop_name']}: {e}")
            
    print("\n----------------------------------------------------")
    print("Reading back updated records from PostgreSQL:")
    print("----------------------------------------------------")
    try:
        # Get all records from database
        records = CropMarketData.all().items
        for idx, rec in enumerate(records):
            print(f"{idx+1}. {rec.get('crop_name')} ({rec.get('state')}): ₹{rec.get('price_per_kg')}/kg | Season: {rec.get('season')} | Demand: {rec.get('demand_level')}")
    except Exception as e:
        print(f"Failed to query database records: {e}")

if __name__ == "__main__":
    main()
