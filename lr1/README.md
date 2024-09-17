# Выполнение лабораторной работы №1
## В пятом семестре

1. Были созданы два файла - myremotemodule и activation_script. Они находятся в разных местах.
2. Запуск:
    1. myremotemodule:

        ![Изображение](pic/image0.JPG)
    2. activation_script (у меня получилось не сразу):
  
       ![Изображение](pic/image.png)
    3. Импорт модуля с сервера, [использован GitHub Pages](https://github.com/hbjnmcd/prog5lr1/tree/main). Результат на картинке.

      ![Изображение](pic/image2.jpg)
   
    4. Изменение класса URLLoader и функции url_hook с использованием модуля requests:
```python
class URLLoader:
    def create_module(self, target):
        return None

    def exec_module(self, module):
        response0 = requests.get(module.__spec__.origin)
        source = response0.text

        code = compile(source, module.__spec__.origin, mode="exec")
        exec(code, module.__dict__)

def url_hook(some_str):
    if not some_str.startswith(("http", "https")):
        raise ImportError

    response1 = requests.get(some_str)
    data = response1.text
    filenames = re.findall("[a-zA-Z_][a-zA-Z0-9_]*.py", data)
    modnames = {name[:-3] for name in filenames}
    return URLFinder(some_str, modnames)

```

    5. Для того, чтобы все сработало, сначала нужно было установить requests через pip install. Итог работы:
    
     ![Изображение](pic/image3.jpg)
