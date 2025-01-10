import requests
import json
from my_key import api_key
import matplotlib.pyplot as pplt
import pandas as pd

CITY = "Санкт-Петербург, RU"
LAT = 59.57
LON = 30.19

def getweather(api_key=None):
    """Получение данных о погоде"""
    if api_key:
        try:
            response = requests.get(
                f'http://api.openweathermap.org/data/2.5/forecast?'
                f'lat={LAT}&lon={LON}&appid={api_key}&lang=ru&units=metric'
            )
            response.raise_for_status()
            req_obj = response.json()
            measures = [{"dt": measure['dt'], "temp": measure['main']['temp']} for measure in req_obj["list"]]
            return json.dumps({'city': CITY, 'temps': measures})
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных о погоде: {e}")
            return None

def visualise_data(json_data):
    """Визуализация данных"""
    data = json.loads(json_data)

    if 'error' in data:
        print(f"Ошибка в данных о погоде: {data['error']}")
        return

    city_name = data['city']
    temps_data = pd.DataFrame(data['temps'])
    temps_data['dt'] = pd.to_datetime(temps_data['dt'], unit='s')

    fig, axes = pplt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [3, 1]})

    # График температуры
    ax1 = axes[0]
    ax1.plot(temps_data['dt'], temps_data['temp'], marker='o', label="Температура", alpha=0.7)
    ax1.set_title(f"Температура в {city_name} за последние дни")
    ax1.set_xlabel("Дата")
    ax1.set_ylabel("Температура (°C)")
    ax1.legend()
    ax1.grid()
    ax1.tick_params(axis='x', rotation=45)

    # Боксплот
    ax2 = axes[1]
    ax2.boxplot(temps_data['temp'], vert=True, patch_artist=True, boxprops=dict(facecolor='skyblue'))
    ax2.set_title("Распределение температуры")
    ax2.set_ylabel("Температура (°C)")

    pplt.tight_layout()
    pplt.show()

weather_data_json = getweather(api_key)
if weather_data_json:
    print(weather_data_json)
    visualise_data(weather_data_json)

