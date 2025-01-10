import os
import base64

# Генерация случайного байтового ключа
secret_key = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
print(f"Сгенерированный секретный ключ: {secret_key}")