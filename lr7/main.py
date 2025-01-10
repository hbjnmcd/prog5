import requests
from xml.etree import ElementTree as ET
import time
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class CurrencyFetcher(metaclass=SingletonMeta):
    def __init__(self):
        self.last_request_time = 0
        self.currencies = []
        self.previous_currencies = []  # Для отслеживания предыдущих данных о валюте
        self.request_interval = 1
        self.observers = []
        self.last_update_time = None
        self.last_update_message = "Курс не изменился"  # Сообщение по умолчанию

    def register_observer(self, observer):
        """Регистрация нового наблюдателя."""
        self.observers.append(observer)

    def notify_observers(self):
        """Уведомление всех наблюдателей о новых данных."""
        for observer in self.observers:
            observer.update(self.currencies, self.last_update_time, self.last_update_message)

    def get_currencies(self, currencies_ids_lst):
        current_time = time.time()
        if current_time - self.last_request_time < self.request_interval:
            raise Exception(f"Запросы можно делать не чаще, чем раз в {self.request_interval} секунд.")

        self.last_request_time = current_time

        response = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
        root = ET.fromstring(response.content)
        self.currencies = []

        invalid_ids = []  # Список для хранения неправильных ID

        for valute in root.findall('Valute'):
            valute_id = valute.get('ID')
            if valute_id in currencies_ids_lst:
                name = valute.find('Name').text
                value = valute.find('Value').text.replace(',', '.')
                charcode = valute.find('CharCode').text
                nominal = int(valute.find('Nominal').text)
                value_per_unit = float(value) / nominal
                self.currencies.append({charcode: (name, f"{value_per_unit:.4f}")})
            else:
                invalid_ids.append(valute_id)

        # Если есть неправильные ID, добавляем их в список, но не выводим в результате
        for invalid_id in invalid_ids:
            self.currencies.append({invalid_id: None})

        # время последнего обновления
        self.last_update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))

        if self.currencies != self.previous_currencies:
            self.last_update_message = f"Курс поменялся {self.last_update_time}"
        else:
            self.last_update_message = "Курс не изменился"

        self.previous_currencies = self.currencies.copy()  # Обновляем предыдущие валюты

        self.notify_observers()  # Уведомляем наблюдателей
        return [currency for currency in self.currencies if
                currency[list(currency.keys())[0]] is not None]
    def manual_update(self, currencies_ids_lst):
        # Обновляем время последнего обновления
        self.last_update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # Обновляем время
        updated_currencies = self.get_currencies(currencies_ids_lst)  # Получаем обновленные валюты

        # Обновляем сообщение о последнем обновлении
        if updated_currencies != self.currencies:
            self.last_update_message = f"Курс поменялся {self.last_update_time}"
        else:
            self.last_update_message = "Курс не изменился"

        self.notify_observers()  # Уведомляем наблюдателей
        return updated_currencies

class CurrencyObserver:
    def __init__(self, socketio):
        self.socketio = socketio

    def update(self, currencies, last_update_time, last_update_message):
        """Метод для получения обновлений от CurrencyFetcher."""
        self.socketio.emit('currency_update', {
            'currencies': currencies,
            'last_update_time': last_update_time,
            'last_update_message': last_update_message  # Отправляем сообщение о обновлении
        })

# Создаем экземпляры классов
currency_fetcher = CurrencyFetcher()
currency_observer = CurrencyObserver(socketio)
currency_fetcher.register_observer(currency_observer)

@app.route('/')
def index():
    # Просто рендерим страницу без вызова get_currencies
    return render_template('index.html', last_update_time=currency_fetcher.last_update_time)

@socketio.on('manual_update')
def handle_manual_update(currencies_ids_lst):
    try:
        currency_fetcher.manual_update(currencies_ids_lst)
    except Exception as e:
        print(e)

def background_task():
    """Фоновая задача для получения валют каждые N секунд."""
    while True:
        try:
            currency_fetcher.get_currencies(['R01235', 'R01239', 'R01270'])  # Пример ID валют
            print(f"Updated currencies at {currency_fetcher.last_update_time}")
        except Exception as e:
            print(e)
        time.sleep(currency_fetcher.request_interval)

if __name__ == '__main__':
    socketio.start_background_task(target=background_task)
    socketio.run(app, allow_unsafe_werkzeug=True)
