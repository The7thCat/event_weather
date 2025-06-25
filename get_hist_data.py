from datetime import datetime, timedelta
from meteostat import Point, Hourly, Stations

# historical data form meteostat

def get_historical_hourly_temperature(lat, lon, hist_start_naive, hist_end_naive, first_available_year, last_available_year):
	historical_city = Point(lat, lon)
	hist_end_naive, hist_start_naive = check_avail_years(first_available_year, last_available_year, hist_end_naive, hist_start_naive)
	data = Hourly(historical_city, hist_start_naive, hist_end_naive)
	hist_weather_data = data.fetch()
	if hist_weather_data.empty:
		print("No data avail. for selected date.")
		return None
	return hist_weather_data

#theory crafting check for earliest available data
def get_avail_dates(lat, lon):
	# location = Point(lat, lon)
	stations = Stations().nearby(lat, lon).fetch(1)
	if stations.empty:
		return None, None
	first_available_year = stations['hourly_start'].min()
	last_available_year = stations['hourly_end'].max()
	return first_available_year, last_available_year

def check_avail_years(first_available_year, last_available_year, hist_end_naive, hist_start_naive):
	while last_available_year < hist_end_naive:
		hist_end_naive -= timedelta(days=365)
	while first_available_year > hist_start_naive:
		hist_start_naive -= timedelta(days=365)
	return hist_end_naive, hist_start_naive
