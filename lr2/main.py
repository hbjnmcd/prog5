from owm_my_key import my_key
from getweatherdata import get_weather_data

if __name__ == '__main__':
    city = input()
    result = get_weather_data(city, my_key)
    print(result)
