import json
import math
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chat_engine import get_chat_response

# Load data at startup
try:
    with open('monuments_data.json', 'r', encoding='utf-8') as f:
        MONUMENTS = json.load(f)
    
    with open('safety_data.json', 'r', encoding='utf-8') as f:
        SAFETY_DATA = json.load(f)
        
    print(f"Loaded {len(MONUMENTS)} monuments and safety data successfully")
    
except FileNotFoundError as e:
    print(f"Error: Required data file not found - {e}")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in data file - {e}")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="India Tourism AI Guide Backend",
    description="REST API for Delhi tourism with AI-powered chat and monument information",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 0.5

class ChatRequest(BaseModel):
    user_message: str
    user_latitude: float
    user_longitude: float

# Utility functions
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in kilometers
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    earth_radius = 6371
    
    # Calculate the distance
    distance = earth_radius * c
    
    return round(distance, 2)

def get_nearby_monuments(lat: float, lon: float, radius_km: float) -> List[dict]:
    """
    Get monuments within specified radius, sorted by distance
    """
    nearby = []
    
    for monument in MONUMENTS:
        distance = haversine_distance(lat, lon, monument['latitude'], monument['longitude'])
        
        if distance <= radius_km:
            monument_copy = monument.copy()
            monument_copy['distance_km'] = distance
            nearby.append(monument_copy)
    
    # Sort by distance (closest first)
    nearby.sort(key=lambda x: x['distance_km'])
    
    return nearby

def get_safety_tips(lat: float, lon: float) -> List[str]:
    """
    Get relevant safety tips based on location
    """
    tips = []
    
    # Add general tips
    tips.extend(SAFETY_DATA.get('general_tips', []))
    
    # Add area-specific tips
    for area in SAFETY_DATA.get('area_specific', []):
        area_distance = haversine_distance(
            lat, lon, 
            area['latitude'], area['longitude']
        )
        
        if area_distance <= area['radius_km']:
            tips.extend(area.get('tips', []))
    
    # Remove duplicates while preserving order
    unique_tips = []
    for tip in tips:
        if tip not in unique_tips:
            unique_tips.append(tip)
    
    return unique_tips

# API Endpoints
@app.get("/")
async def root():
    """
    API information and available endpoints
    """
    return {
        "name": "India Tourism AI Guide Backend",
        "version": "1.0.0",
        "description": "REST API for Delhi tourism with AI-powered chat and monument information",
        "endpoints": [
            "GET / - API information",
            "GET /health - Health check",
            "POST /api/check-location - Find nearby monuments",
            "GET /api/monument/{monument_id} - Get monument details",
            "GET /api/monuments/all - Get all monuments",
            "POST /api/safety-tips - Get location-based safety tips",
            "POST /api/chat - AI-powered chat with tour guide"
        ]
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "monuments_loaded": len(MONUMENTS),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/check-location")
async def check_location(request: LocationRequest):
    """
    Find monuments near the given location
    """
    nearby_monuments = get_nearby_monuments(
        request.latitude, 
        request.longitude, 
        request.radius_km
    )
    
    return {
        "success": True,
        "location": {
            "latitude": request.latitude,
            "longitude": request.longitude,
            "radius_km": request.radius_km
        },
        "monuments_found": len(nearby_monuments),
        "monuments": nearby_monuments
    }

@app.get("/api/monument/{monument_id}")
async def get_monument(monument_id: str):
    """
    Get detailed information about a specific monument
    """
    for monument in MONUMENTS:
        if monument['id'] == monument_id:
            return {
                "success": True,
                "monument": monument
            }
    
    raise HTTPException(status_code=404, detail="Monument not found")

@app.get("/api/monuments/all")
async def get_all_monuments():
    """
    Get all available monuments
    """
    return {
        "success": True,
        "total_monuments": len(MONUMENTS),
        "monuments": MONUMENTS
    }

@app.post("/api/safety-tips")
async def get_safety_tips_endpoint(request: LocationRequest):
    """
    Get safety tips based on location (uses 1.0 km radius internally)
    """
    # Get nearby monuments for monument-specific warnings
    nearby_monuments = get_nearby_monuments(request.latitude, request.longitude, 1.0)
    
    # Get location-based safety tips
    location_tips = get_safety_tips(request.latitude, request.longitude)
    
    # Add monument-specific warnings
    monument_warnings = []
    for monument in nearby_monuments[:2]:  # Max 2 monuments
        warnings = monument.get('safety_warnings', [])
        for warning in warnings:
            if warning not in monument_warnings:
                monument_warnings.append(f"{monument['name']}: {warning}")
    
    all_tips = monument_warnings + location_tips
    
    return {
        "success": True,
        "location": {
            "latitude": request.latitude,
            "longitude": request.longitude
        },
        "nearby_monuments": len(nearby_monuments),
        "safety_tips": all_tips,
        "emergency_contacts": SAFETY_DATA.get('emergency_contacts', {}),
        "transportation_scams": SAFETY_DATA.get('transportation_scams', []),
        "shopping_scams": SAFETY_DATA.get('shopping_scams', [])
    }

@app.post("/api/chat")
async def chat_with_guide(request: ChatRequest):
    """
    Chat with AI tour guide
    """
    # Get nearby monuments (0.5 km radius for chat context)
    nearby_monuments = get_nearby_monuments(
        request.user_latitude, 
        request.user_longitude, 
        0.5
    )
    
    # Get chat response
    chat_result = get_chat_response(
        request.user_message,
        nearby_monuments,
        request.user_latitude,
        request.user_longitude
    )
    
    # Determine current location context
    current_location = "Unknown"
    distance_km = None
    
    if nearby_monuments:
        nearest = nearby_monuments[0]
        current_location = nearest['name']
        distance_km = nearest['distance_km']
    
    return {
        "success": True,
        "response": chat_result["response"],
        "ai_powered": chat_result["ai_powered"],
        "nearby_monuments": nearby_monuments[:3],  # Max 3 for context
        "context": {
            "current_location": current_location,
            "distance_km": distance_km
        }
    }

# Entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)