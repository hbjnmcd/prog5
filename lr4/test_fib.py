from gen_fib import EvenNumbersIterator, my_genn
import pytest

def test_fib_1():
    gen = my_genn()
    assert gen.send(3) == [0, 1, 1], "Тривиальный случай n = 3, список [0, 1, 1]"


def test_fib_2():
    gen = my_genn()
    assert gen.send(5) == [0, 1, 1, 2, 3], "Пять первых членов ряда"


def test_fib_3():
    gen = my_genn()
    assert gen.send(0) == [], "Тест на ноль элементов, результат должен быть пустым списком"


def test_fib_4():
    gen = my_genn()
    assert gen.send(1) == [0], "Тест на один элемент, результат должен быть [0]"


def test_fib_5():
    gen = my_genn()
    assert gen.send(2) == [0, 1], "Тест на два элемента, результат должен быть [0, 1]"


def test_even_numbers_iterator_with_fib():
    lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 13]
    fib_iterator = EvenNumbersIterator(lst)
    assert list(fib_iterator) == [0, 1, 2, 3, 5, 8, 13], "Должны быть извлечены все числа Фибоначчи из списка"


def test_even_numbers_iterator_with_no_fib_1():
    lst = [4, 6, 8, 10]
    fib_iterator = EvenNumbersIterator(lst)
    assert list(fib_iterator) == [], "Список не содержит чисел Фибоначчи, результат должен быть пустым списком"

def test_even_numbers_iterator_with_multiple_fibs():
    lst = [0, 1, 2, 3, 5, 8, 13, 21]
    fib_iterator = EvenNumbersIterator(lst)
    assert list(fib_iterator) == [0, 1, 2, 3, 5, 8, 13, 21], "Все числа в списке являются числами Фибоначчи"
