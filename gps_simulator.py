#!/usr/bin/env python3
"""
GPS Location Simulator for India Tourism API
Simulates a tourist walking through Delhi with real GPS coordinates
"""

import requests
import json
import time

# API endpoint
API_BASE = "http://localhost:8001"

# Real GPS coordinates for Delhi monuments
LOCATIONS = {
    "India Gate": {"lat": 28.6129, "lon": 77.2295},
    "Red Fort": {"lat": 28.6562, "lon": 77.2410},
    "Jama Masjid": {"lat": 28.6507, "lon": 77.2334},
    "Qutub Minar": {"lat": 28.5244, "lon": 77.1855},
    "Lotus Temple": {"lat": 28.5535, "lon": 77.2588},
    "Humayun's Tomb": {"lat": 28.5933, "lon": 77.2507},
    "Connaught Place": {"lat": 28.6315, "lon": 77.2167},
    "Chandni Chowk": {"lat": 28.6506, "lon": 77.2303}
}

def test_location(name, lat, lon):
    """Test API with specific GPS coordinates"""
    print(f"\n📍 SIMULATING GPS: {name}")
    print(f"   Coordinates: {lat}, {lon}")
    
    # Check nearby monuments
    response = requests.post(f"{API_BASE}/api/check-location", 
                           json={"latitude": lat, "longitude": lon, "radius_km": 1.0})
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {data['monuments_found']} nearby monuments:")
        for monument in data['monuments'][:2]:  # Show top 2
            print(f"   • {monument['name']} - {monument['distance_km']} km away")
    
    # Test chat at this location
    chat_response = requests.post(f"{API_BASE}/api/chat",
                                json={
                                    "user_message": "What's nearby?",
                                    "user_latitude": lat,
                                    "user_longitude": lon
                                })
    
    if chat_response.status_code == 200:
        chat_data = chat_response.json()
        print(f"   🤖 Guide says: {chat_data['response'][:100]}...")

def simulate_tourist_journey():
    """Simulate a tourist's GPS journey through Delhi"""
    print("🚶‍♂️ SIMULATING TOURIST GPS JOURNEY THROUGH DELHI")
    print("=" * 60)
    
    # Tourist route: India Gate → Red Fort → Jama Masjid → Qutub Minar
    route = ["India Gate", "Red Fort", "Jama Masjid", "Qutub Minar"]
    
    for location in route:
        coords = LOCATIONS[location]
        test_location(location, coords["lat"], coords["lon"])
        time.sleep(1)  # Simulate walking time

def test_safety_by_area():
    """Test safety warnings for different Delhi areas"""
    print("\n🛡️ TESTING AREA-SPECIFIC SAFETY WARNINGS")
    print("=" * 50)
    
    areas = {
        "Paharganj (Budget Hotels)": {"lat": 28.6455, "lon": 77.2176},
        "Old Delhi (Chandni Chowk)": {"lat": 28.6506, "lon": 77.2303},
        "South Delhi (Upscale)": {"lat": 28.5535, "lon": 77.2588},
        "Connaught Place (Central)": {"lat": 28.6315, "lon": 77.2167}
    }
    
    for area_name, coords in areas.items():
        print(f"\n📍 {area_name}")
        response = requests.post(f"{API_BASE}/api/safety-tips",
                               json={"latitude": coords["lat"], "longitude": coords["lon"]})
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Safety tips: {len(data['safety_tips'])} warnings")
            # Show first 2 area-specific tips
            for tip in data['safety_tips'][-3:]:  # Last 3 are usually area-specific
                if len(tip) < 80:  # Show shorter tips
                    print(f"   ⚠️  {tip}")

if __name__ == "__main__":
    try:
        # Test if API is running
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ API is running!")
            simulate_tourist_journey()
            test_safety_by_area()
        else:
            print("❌ API not responding")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure server is running on port 8001")