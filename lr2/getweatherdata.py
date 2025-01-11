import requests
import json


def format_utc_offset(timezone_offset):
    hours_offset = timezone_offset // 3600  # Преобразуем смещение в секундах в часы
    # Форматируем строку UTC±N
    return f"UTC{'+' if hours_offset >= 0 else ''}{hours_offset}"


def get_weather_data(place, api_key=None):
    if not api_key:
        return None
    if not place:
        return None
    url = f'https://api.openweathermap.org/data/2.5/weather?q={place}&appid={api_key}&units=metric'
    r = requests.get(url).json()
    city_info = {
        'name': r['name'],
        'country_code': r['sys']['country'],
        'coord': {
            'lon': r['coord']['lon'],
            'lat': r['coord']['lat']
        },
        'timezone': format_utc_offset(r['timezone']),
        'temperature': r['main']['temp'],
        'feels_like': r['main']['feels_like']
    }
    res = json.dumps(city_info, ensure_ascii=False, indent=4)

    return res

