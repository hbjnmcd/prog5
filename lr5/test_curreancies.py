import pytest
from main import CurrencyFetcher
import time


@pytest.fixture
def currency_fetcher():
    """Фикстура для создания экземпляра CurrencyFetcher перед каждым тестом."""
    return CurrencyFetcher()

def test_invalid_currency_id(currency_fetcher):
    # Тест на неправильный ID
    result = currency_fetcher.get_currencies(['R9999'])
    # Проверяем, что возвращается пустой список валидных валют
    time.sleep(15)
    assert result == []  # В результате не должно быть валидных валют

def test_valid_currency_id(currency_fetcher):
    # Тест на корректные ID
    # Запрашиваем обе валюты одновременно
    result = currency_fetcher.get_currencies(['R01035', 'R01335'])  # GBP и KZT

    # Проверяем, что вернулось две валюты
    assert len(result) == 2

    # Проверяем названия валют и диапазон значений
    for currency in result:
        charcode = list(currency.keys())[0]
        name, value = currency[charcode]

        assert isinstance(name, str)  # Название должно быть строкой

        # Преобразуем value в float для проверки
        value = float(value)

        assert value >= 0  # Проверяем, что значение не отрицательное
        assert value <= 999  # Проверяем, что значение не больше 999
