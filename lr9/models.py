from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    spending = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# Функция для определения уровня бонуса
def determine_bonus_level(spending):
    levels = {
        "Серебряный уровень": (0, 100),
        "Золотой уровень": (100, 500),
        "Платиновый уровень": (500, float('inf'))
    }

    for level, (min_spending, max_spending) in levels.items():
        if min_spending <= spending < max_spending:
            return level, min_spending, max_spending

    return None, None, None  # На случай, если уровень не найден