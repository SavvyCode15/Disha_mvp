# India Tourism AI Guide Backend

A Python REST API backend for a mobile tourist-guide app focused on Delhi, India. This backend provides nearby monument information, detailed historical data, safety warnings, and conversational chat responses powered by Groq's free LLM API.

## What This Is

This is the "brain" of a mobile tourism app that receives GPS coordinates from users and returns comprehensive information about nearby Delhi monuments, including AI-powered conversational responses, safety tips, pricing information, and cultural insights. The system uses Groq's free LLM service with intelligent fallback to rule-based responses, ensuring users never encounter errors.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- A free Groq API key from [console.groq.com](https://console.groq.com) (no credit card required)

## Setup

Follow these exact commands to set up the project:

```bash
git clone <url>
cd india-tour-guide
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and paste your Groq API key
python main.py
# Open http://localhost:8000
```

## How to Get Groq API Key (Free)

1. Go to https://console.groq.com
2. Sign up (no credit card needed)
3. Go to API Keys → Create new key
4. Copy the key into your .env file

The free tier provides 14,400 requests per day with extremely fast response times (300+ tokens/second).

## Test with curl

Here are 5 ready-to-copy test commands:

### 1. Chat greeting near India Gate
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Hello, where am I?",
    "user_latitude": 28.6129,
    "user_longitude": 77.2295
  }'
```

### 2. Check location near Red Fort (radius 1.0)
```bash
curl -X POST "http://localhost:8000/api/check-location" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 28.6562,
    "longitude": 77.2410,
    "radius_km": 1.0
  }'
```

### 3. Monument info: GET /api/monument/red-fort
```bash
curl -X GET "http://localhost:8000/api/monument/red-fort"
```

### 4. Safety tips in Old Delhi
```bash
curl -X POST "http://localhost:8000/api/safety-tips" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 28.6507,
    "longitude": 77.2334,
    "radius_km": 1.0
  }'
```

### 5. Chat: "how much is the ticket" near Qutub Minar
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "how much is the ticket?",
    "user_latitude": 28.5244,
    "user_longitude": 77.1855
  }'
```

## Deploy to Render.com (Free)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service → connect your repo
3. Configure the service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable in Render's Environment tab:
   - **Key**: `GROQ_API_KEY`
   - **Value**: your Groq API key
5. Select Free tier → Deploy

Your API will be live at `https://your-app-name.onrender.com` within 5 minutes.

## How to Add a New Monument

1. Add a new monument object to `monuments_data.json` following the existing schema
2. Ensure all required fields are included: id, name, latitude, longitude, category, description, audio_script, etc.
3. Push changes to GitHub
4. Render will automatically redeploy with the new monument

## API Endpoints

- `GET /` - API information and endpoint list
- `GET /health` - Health check with monument count
- `POST /api/check-location` - Find nearby monuments
- `GET /api/monument/{monument_id}` - Get specific monument details
- `GET /api/monuments/all` - Get all monuments
- `POST /api/safety-tips` - Get location-based safety tips
- `POST /api/chat` - AI-powered chat with tour guide

## Features

- **8 Delhi Monuments**: Red Fort, Qutub Minar, India Gate, Humayun's Tomb, Lotus Temple, Jama Masjid, Akshardham Temple, Lodhi Garden
- **AI Chat**: Powered by Groq's llama-3.3-70b-versatile model with rule-based fallback
- **Location-Based**: GPS coordinate input with distance calculations
- **Safety Information**: Area-specific scam warnings and safety tips
- **Cultural Insights**: Audio scripts, pricing, timings, and local recommendations
- **Zero Downtime**: Intelligent fallback ensures users never see errors

## Cost: $0/month

- **Groq API**: Free tier (14,400 requests/day, no credit card)
- **Render Hosting**: Free tier (750 hours/month)
- **No Database**: JSON files loaded into memory
- **Open Source**: All code and data included

## Architecture

- **Framework**: FastAPI with automatic Swagger documentation
- **LLM**: Groq API (llama-3.3-70b-versatile) with rule-based fallback
- **Data**: JSON files for monuments and safety information
- **Distance**: Haversine formula for GPS calculations
- **Deployment**: Render.com with automatic GitHub integration

The system is designed for reliability, speed, and zero cost while providing comprehensive tourism information for Delhi visitors.