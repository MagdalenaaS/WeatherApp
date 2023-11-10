from django.shortcuts import render
import requests
from datetime import datetime

def index(request):
    API_KEY = "9603b12184efc143aa7d0b7680ceaebe"
    current_weather_url = "https://api.openweathermap.org/data/2.5/weather"
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    if request.method == "POST":
        city = request.POST["city"].capitalize()
        if not city:
            return render(request, "weatherapp/index.html")

        parameters = {
            "q": city, 
            "appid": API_KEY,
            "units": "metric"
        }

        current_weather_data = fetch_current_weather(city, API_KEY, current_weather_url, parameters)
        forecast = fetch_forecast(city, API_KEY, forecast_url, parameters)

        return render(request, "weatherapp/index.html", {'current_weather_data': current_weather_data, 'forecast': forecast})

    else:
        return render(request, "weatherapp/index.html")


def fetch_current_weather(city, api_key, url, parameters):
    response = requests.get(url=url, params=parameters).json()

    if 'cod' in response and response['cod'] == '404':
        return {"error": "Invalid city name"}

    current_weather_data = {
        "day": datetime.now().strftime('%A'),
        "city": city,
        "description": response.get("weather", [{}])[0].get("description", ""),
        "temp": response.get("main", {}).get("temp", ""),
        "icon": response.get("weather", [{}])[0].get("icon", ""),
    }
    return current_weather_data


def fetch_forecast(city, api_key, url, parameters):
    response = requests.get(url=url, params=parameters).json()
    if 'list' in response:
        forecast_data = response['list']
        daily_forecast = {}
        for day in forecast_data:
            date = datetime.utcfromtimestamp(day['dt']).strftime('%Y-%m-%d')
            if date not in daily_forecast:
                daily_forecast[date] = {
                    "day": datetime.fromtimestamp(day['dt']).strftime('%A'),
                    "min_temp": round(day['main']['temp_min']),
                    "max_temp": round(day['main']['temp_max']),
                    "description": day['weather'][0]['description'],
                    "icon": day['weather'][0]['icon'],
                }
            else:
                min_temp = round(day['main']['temp_min'])
                max_temp = round(day['main']['temp_max'])
                if min_temp < daily_forecast[date]['min_temp']:
                    daily_forecast[date]['min_temp'] = min_temp
                if max_temp > daily_forecast[date]['max_temp']:
                    daily_forecast[date]['max_temp'] = max_temp
        
        five_day_forecast = list(daily_forecast.values())

        return five_day_forecast
    else:
        return []
    