import requests
from datetime import datetime, timezone, timedelta

# OpenCage Geocoding API key
geocoding_api_key = '55d1aa2147d0467faef280fc038594d3'

def get_lat_lon(location_name, api_key):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location_name}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if data['results']:
        latitude = data['results'][0]['geometry']['lat']
        longitude = data['results'][0]['geometry']['lng']
        return latitude, longitude
    else:
        raise ValueError("Location not found")

def get_sunrise_sunset_times(location, date):
    latitude, longitude = location
    url = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&date={date}&formatted=0"
    response = requests.get(url)
    data = response.json()
    
    def fix_iso_format(time_str):
        if len(time_str) > 19 and time_str[19] == ':':
            return time_str
        if len(time_str) == 20 and time_str[19] != ':':
            return time_str[:19] + ':00' + time_str[19:]
        return time_str
    
    sunrise_time_str = fix_iso_format(data['results']['sunrise'])
    sunset_time_str = fix_iso_format(data['results']['sunset'])
    
    sunrise_time = datetime.fromisoformat(sunrise_time_str).astimezone(timezone.utc)
    sunset_time = datetime.fromisoformat(sunset_time_str).astimezone(timezone.utc)
    
    return sunrise_time, sunset_time

def get_weather_data(location, api_key):
    latitude, longitude = location
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    weather_data = {
        'cloud_cover': data['weather'][0]['main'],  # 'Clear', 'Clouds', 'Rain', etc.
        'humidity': data['main']['humidity'],
        'temperature': data['main']['temp'],
        'wind_speed': data['wind']['speed']
    }
    return weather_data

def calculate_quality(weather_data, event_time):
    now = datetime.now(timezone.utc)
    
    # Calculate time difference
    time_diff = abs((event_time - now).total_seconds())
    
    # Adjust the weight of time difference in the final rating
    time_weight = max(0, 10 - (time_diff / 3600))  # Reducing weight if too far from the event
    
    # Score cloud cover
    cloud_cover = weather_data['cloud_cover']
    cloud_score = 0
    if cloud_cover in ['Clear']:
        cloud_score = 10
    elif cloud_cover in ['Few clouds', 'Scattered clouds']:
        cloud_score = 7
    elif cloud_cover == 'Broken clouds':
        cloud_score = 4
    elif cloud_cover == 'Overcast clouds':
        cloud_score = 1
    
    # Since OpenWeatherMap free tier does not include AQI, we'll assume a default moderate value
    air_quality_index = 50
    air_quality_score = 5
    
    # Score humidity
    humidity = weather_data['humidity']
    humidity_score = 0
    if 30 <= humidity <= 50:
        humidity_score = 10
    elif 50 <= humidity <= 70:
        humidity_score = 5
    
    # Score temperature
    temperature = weather_data['temperature']
    temperature_score = 0
    if 15 <= temperature <= 25:
        temperature_score = 10
    
    # Score wind speed
    wind_speed = weather_data['wind_speed']
    wind_score = 0
    if 0 <= wind_speed <= 10:
        wind_score = 10
    
    # Compute total score
    total_score = cloud_score + air_quality_score + humidity_score + temperature_score + wind_score + time_weight
    
    # Define the maximum possible score
    max_score = 10 + 5 + 10 + 10 + 10 + 10  # Sum of all maximum scores including time weight
    
    # Calculate the rating on a scale of 1-100
    rating = (total_score / max_score) * 100
    rating = max(1, min(100, int(rating)))  # Ensure rating is between 1 and 100
    
    return rating

def predict_sunrise_sunset_quality(location_name, weather_api_key, date=None):
    # Get the latitude and longitude for the location name
    location = get_lat_lon(location_name, geocoding_api_key)
    
    # Get the specified date, default to today's date if not provided
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Calculate sunrise and sunset times
    sunrise_time, sunset_time = get_sunrise_sunset_times(location, date)
    
    # Retrieve weather data
    weather_data = get_weather_data(location, weather_api_key)
    
    # Calculate quality for sunrise and sunset
    sunrise_quality = calculate_quality(weather_data, sunrise_time)
    sunset_quality = calculate_quality(weather_data, sunset_time)
    
    return sunrise_quality, sunset_quality

# usage
location_name = "Frankston"  # Example location
weather_api_key = '60d55d74511ed95d2ec07c44b354f209'  # Your OpenWeatherMap API key

# Get today's sunrise and sunset quality
sunrise_quality_today, sunset_quality_today = predict_sunrise_sunset_quality(location_name, weather_api_key)
#print(f"Today's predicted sunrise quality rating for {location_name} is: {sunrise_quality_today}")
#print(f"Today's predicted sunset quality rating for {location_name} is: {sunset_quality_today}")

# Get tomorrow's date
tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

# Get tomorrow's sunrise and sunset quality
sunrise_quality_tomorrow, sunset_quality_tomorrow = predict_sunrise_sunset_quality(location_name, weather_api_key, tomorrow_date)
#print(f"Tomorrow's predicted sunrise quality rating for {location_name} is: {sunrise_quality_tomorrow}")
#print(f"Tomorrow's predicted sunset quality rating for {location_name} is: {sunset_quality_tomorrow}")
