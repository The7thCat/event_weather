from datetime import datetime, time
from meteostat import Point, Hourly

# historical data form meteostat

def get_historical_hourly_temperature(lat, lon, start_naive, end_naive):
	historical_city = Point(lat, lon)
	data = Hourly(historical_city, start_naive, end_naive)
	data = data.fetch()