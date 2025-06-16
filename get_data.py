import requests
from dotenv import load_dotenv
from datetime import datetime
import os
import pandas as pd

# ToS MET Norway for forecast data
load_dotenv()
CONTACT_EMAIL = os.getenv("MET_NO_EMAIL")

HEADERS = {"User-Agent": f"MyApp/1.0 ({CONTACT_EMAIL})", "From": CONTACT_EMAIL}


def get_coordinates(city):
	url = f"https://nominatim.openstreetmap.org/search"
	params = {
		"q": city,
		"format": "json",
		"limit": 1,
		"addressdetails": 1,
	}
	try:
		response = requests.get(
			url, params=params, headers=HEADERS
		)
		response.raise_for_status()
		results = response.json()
		if not results:
			return None, None, None
		data = results[0]
		lat = float(data["lat"])
		lon = float(data["lon"])
		country_code = data["address"].get("country_code", "").upper()
		return lat, lon, country_code
	except Exception as e:
		print(f"Error while fetching coordinates: {e}")
		return None, None, None
		
def fetch_weather_data(lat, lon, user_agent):
		url = f"https://api.met.no/weatherapi/locationforecast/2.0/complete?lat={lat}&lon={lon}"
		headers = {"User-Agent": user_agent or "example@example.com"}
		response = requests.get(url, headers=headers)
		# successful HTTP request
		if response.status_code == 200:
			return response.json()
		return None

def extract_hourly_weather(weather_json, start_dt, end_dt):
    timeseries = weather_json.get("properties", {}).get("timeseries", [])
    hourly_data = []
    for entry in timeseries:
        time_str = entry["time"].replace("Z", "+00:00")
        time = datetime.fromisoformat(time_str)  # offset-aware
        if start_dt <= time <= end_dt:
            temp = entry["data"]["instant"]["details"].get("air_temperature")
            hourly_data.append({"time": time, "temperature": temp})
    return pd.DataFrame(hourly_data)