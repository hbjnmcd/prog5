from main import CurrencyFetcher
import json
import csv
import io
import time


class CurrenciesList:
    def __init__(self):
        self.fetcher = CurrencyFetcher()

    def get_currencies(self, currencies_ids_lst):
        return self.fetcher.get_currencies(currencies_ids_lst)


class CurrencyDecorator:
    def __init__(self, currencies_list):
        self._currencies_list = currencies_list

    def get_currencies(self, currencies_ids_lst):
        return self._currencies_list.get_currencies(currencies_ids_lst)

class ConcreteDecoratorJSON(CurrencyDecorator):
    def get_currencies(self, currencies_ids_lst):
        data = super().get_currencies(currencies_ids_lst)
        return json.dumps(data, ensure_ascii=False, indent=1)

class ConcreteDecoratorCSV(CurrencyDecorator):
    def __init__(self, currencies_list):
        self._currencies_list = currencies_list

    def get_currencies(self, currencies_ids_lst):
        currencies = self._currencies_list.get_currencies(currencies_ids_lst)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['CharCode', 'Name', 'Value'])  # Заголовки
        for currency in currencies:
            charcode = list(currency.keys())[0]
            name, value = currency[charcode]
            writer.writerow([charcode, name, value])

        return output.getvalue()


currencies_list = CurrenciesList()

try:
    result = currencies_list.get_currencies(['R01035', 'R01335', 'R01700J'])
    print("Базовая версия:")
    print(result)

    time.sleep(5)
    # Декоратор для JSON
    json_currencies = ConcreteDecoratorJSON(currencies_list)
    print("\nДанные в формате JSON:")
    print(json_currencies.get_currencies(['R01035', 'R01335', 'R01700J']))

    time.sleep(5)
    # Декоратор для CSV
    csv_currencies = ConcreteDecoratorCSV(currencies_list)
    print("\nДанные в формате CSV:")
    print(csv_currencies.get_currencies(['R01035', 'R01335', 'R01700J']))

except Exception as e:
    print(e)