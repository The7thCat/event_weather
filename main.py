import streamlit as st
import os
from datetime import time, date, timedelta, datetime, timezone
from get_data import get_coordinates, fetch_weather_data, extract_hourly_weather
from get_hist_data import get_historical_hourly_temperature, get_avail_dates
import pandas as pd
import plotly.express as px

# Terms of service MET Weather API (MET Norway)
USER_AGENT_EMAIL = os.getenv("MET_NO_EMAIL")

# UI Streamlit
st.title("Event weather history and forecast")

# Data input
city = st.text_input("Enter a city name")
event_start_time = st.time_input("Start time", value=time(9, 0))
event_start_date = st.date_input("Start date", value=date.today(), min_value=date.today())

#limit forecast range to 9 days
max_event_end_date = event_start_date + timedelta(days=9)
event_end_date = st.date_input(
	"End date", value=event_start_date,
	min_value=event_start_date,
	max_value=max_event_end_date,
							   )

# formating date + time to UTC timezone
start_datetime_utc = datetime.combine(event_start_date, event_start_time).replace(
	tzinfo=timezone.utc
)
end_datetime_utc = datetime.combine(event_end_date, time(23, 0)).replace(tzinfo=timezone.utc)

# format time for meteostat
start_naive = start_datetime_utc.replace(tzinfo=None)
end_naive = end_datetime_utc.replace(tzinfo=None)

# calc difference
event_length = end_naive - start_naive

# define years for historical forecast, default 10y
hist_start_naive = start_naive + timedelta(days=3650)
hist_end_naive = end_naive + timedelta(days=3650)

# Buttons
col1, col2, col3 = st.columns([1, 1, 1])
forecast_button = col1.button("Get forecast", use_container_width=True)
historical_button = col2.button("Get historical data", use_container_width=True)

if forecast_button:
	if city:
		lat, lon, country_code = get_coordinates(city)
		if lat is None or lon is None:
			st.error("City not found.")
		else:
			city_display = f"{city}, {country_code}" if country_code else city
			st.success(f"selected city: {city_display}")

			# Fetch weatherdata from MET Norway
			user_agent_email = os.getenv("MET_NO_EMAIL")
			weather_json = fetch_weather_data(lat, lon, user_agent_email)

			if weather_json:
				df = extract_hourly_weather(weather_json, start_datetime_utc, end_datetime_utc)
				if df.empty:
					st.warning("Unable to find weather data.")
				else:
					df["date"] = df["time"].dt.date
					total_days = (event_end_date - event_start_date).days + 1
					days_list = [
						event_start_date + timedelta(days=i) for i in range(total_days)
					]
					# splits days into single days
					for single_date in days_list:
						day_df = df[df["date"] == single_date]
						if day_df.empty:
							st.write(f"No data for {single_date.strftime('%A, %d.%m.%Y')}")
							continue

						fig = px.line(
							day_df,
							x="time",
							y="temperature",
							markers = True,
							labels={"time": "Local time", "temperature": "Temperature (°C)"},
							title=f"Weather on {single_date.strftime('%A, %d.%m.%Y')}",
						)
						fig.update_xaxes(
							tickformat="%H:%M",
							range=[
								datetime.combine(single_date, event_start_time),
								datetime.combine(single_date, time(23, 59, 59)),
							]
						)
						st.plotly_chart(fig, use_container_width=True)

# historical weather date

if historical_button:
	if city:
		lat, lon, country_code = get_coordinates(city)
		if lat is None or lon is None:
			st.error("City not found.")
		else:
			first_available_year, last_available_year = get_avail_dates(lat, lon)
			hist_df = get_historical_hourly_temperature(lat, lon, hist_start_naive, hist_end_naive, first_available_year, last_available_year)
			if first_available_year is None or last_available_year is None:
				st.warning("No station data available.")
			else:
				total_days = (event_end_date - event_start_date).days + 1
				days_list = [event_start_date + timedelta(days=i) for i in range(total_days)]

				for single_date in days_list:
					day_df = hist_df[hist_df["date"] == single_date]
					if day_df.empty:
						st.write(f"No historical data for {single_date.strftime('%A, %d.%m.%Y')}")
						continue

					fig = px.line(
						day_df,
						x="time",
						y="temperature",
						labels={"time": "Local time", "temperature": "Temperature (°C)"},
						title=f"Historical weather on {single_date.strftime('%A, %d.%m.%Y')}",
					)
					fig.update_xaxes(tickformat="%H:%M")
					st.plotly_chart(fig, use_container_width=True)

# with col3:
# 	if st.button("Documentation", use_container_width=True):
