import os

# Configuration for Project Samarth

# Data.gov.in API Configuration
DATA_GOV_API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"  # Public demo key
DATA_GOV_BASE_URL = "https://api.data.gov.in"

# OpenAI Configuration (optional - for advanced NLP)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Set this environment variable if you have OpenAI API

# Cache Configuration
CACHE_DURATION_SECONDS = 3600  # 1 hour for most data
PRICE_CACHE_DURATION_SECONDS = 1800  # 30 minutes for price data

# Known Dataset Resource IDs from data.gov.in
DATASET_IDS = {
    "crop_production": "9ef84268-d588-465a-a308-a864a43d0070",
    "rainfall_data": "88f7c9b1-4a8f-4c8e-b4e1-7c8b9a0f1e2d",  # Placeholder - need to find correct rainfall dataset
    "market_prices": "current-daily-price-various-commodities-various-markets-mandis",
    "weather_stations": "station-wise-dust-storm-events"
}

# Supported entities for query processing
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

MAJOR_CROPS = [
    "Rice", "Wheat", "Cotton", "Sugarcane", "Maize", "Bajra", "Jowar", 
    "Pulses", "Oilseeds", "Groundnut", "Soybean", "Mustard", "Sunflower",
    "Barley", "Gram", "Tur", "Moong", "Urad", "Lentil", "Chickpea"
]