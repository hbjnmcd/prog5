import functools


def fib_elem_gen():
    """Генератор, возвращающий элементы ряда Фибоначчи"""
    a = 0
    b = 1

    while True:
        yield a
        res = a + b
        a = b
        b = res

def my_genn():
    """Сопрограмма"""

    while True:
        number_of_fib_elem = yield
        fib_gen = fib_elem_gen()
        l = [next(fib_gen) for i in range(number_of_fib_elem)]
        yield l


def fib_coroutine(g):
    @functools.wraps(g)
    def inner(*args, **kwargs):
        gen = g(*args, **kwargs)
        gen.send(None)
        return gen
    return inner


class EvenNumbersIterator():
    def __init__(self, instance):
        self.instance = instance  # Исходный список
        self.fib_gen = fib_elem_gen()  # Генератор чисел Фибоначчи
        self.fib_set = set()  # Множество для хранения чисел Фибоначчи
        self.max_num = max(instance)  # Максимальное значение из входного списка
        self.populate_fib_set()  # Заполняем множество

    def populate_fib_set(self):
        """Заполняет множество чисел Фибоначчи до max_num"""
        while True:
            fib_num = next(self.fib_gen)  # Получаем следующее число Фибоначчи
            if fib_num > self.max_num:  # Если больше максимального, выходим
                break
            self.fib_set.add(fib_num)  # Добавляем число в множество

    def __iter__(self):
        return self  # Возвращаем экземпляр класса, реализующего протокол итераторов

    def __next__(self):
        for res in self.instance:
            if res in self.fib_set:  # Проверяем, принадлежит ли число ряду Фибоначчи
                self.instance.remove(res)  # Удаляем элемент, чтобы избежать повторов
                return res
        raise StopIteration  # Если элементов больше нет, вызываем StopIteration


my_genn = fib_coroutine(my_genn)
gen = my_genn()
num = int(input())
print(gen.send(num))

lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 13]
fib_iterator = EvenNumbersIterator(lst)

print("Элементы ряда Фибоначчи из списка:", list(fib_iterator))
