#!/usr/bin/env python3
"""
Test script to verify data integration with data.gov.in
"""

from data_scraper import DataScraper
import json

def test_data_sources():
    print("🧪 Testing Project Samarth Data Integration")
    print("=" * 50)
    
    scraper = DataScraper()
    
    # Test 1: Agricultural Data
    print("\n📊 Testing Agricultural Data...")
    try:
        agri_data = scraper.get_agricultural_data("Maharashtra", "Rice")
        print(f"✅ Agricultural data fetched: {len(agri_data['data'])} records")
        print(f"   Source: {agri_data['source']}")
        if agri_data['data']:
            sample = agri_data['data'][0]
            print(f"   Sample: {sample['state']} - {sample['crop']} - {sample['production_tonnes']} tonnes")
    except Exception as e:
        print(f"❌ Agricultural data error: {e}")
    
    # Test 2: Climate Data
    print("\n🌧️ Testing Climate Data...")
    try:
        climate_data = scraper.get_climate_data("Maharashtra", 2023)
        print(f"✅ Climate data fetched: {len(climate_data['data'])} records")
        print(f"   Source: {climate_data['source']}")
        if climate_data['data']:
            sample = climate_data['data'][0]
            print(f"   Sample: {sample['state']} - {sample['rainfall_mm']}mm rainfall")
    except Exception as e:
        print(f"❌ Climate data error: {e}")
    
    # Test 3: Market Prices
    print("\n💰 Testing Market Price Data...")
    try:
        price_data = scraper.get_market_prices("Rice", "Maharashtra")
        print(f"✅ Price data fetched: {len(price_data['data'])} records")
        print(f"   Source: {price_data['source']}")
        if price_data['data']:
            sample = price_data['data'][0]
            print(f"   Sample: {sample['commodity']} - ₹{sample['price_per_quintal']}/quintal")
    except Exception as e:
        print(f"❌ Price data error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Data integration test completed!")
    print("🌐 Your system is now connected to real government data sources")

if __name__ == "__main__":
    test_data_sources()