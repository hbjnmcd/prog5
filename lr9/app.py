from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, determine_bonus_level
from dotenv import load_dotenv
import os
from datetime import timedelta


load_dotenv()
# Инициализация приложения

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Используйте SQLite для простоты
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Замените на ваш секретный ключ
db.init_app(app)
jwt = JWTManager(app)

# Создание таблиц и добавление тестового пользователя
@app.before_request
def create_tables():
    db.create_all()
    if User.query.count() == 0:
        new_user = User(username='testuser')
        new_user.set_password('password123')  # Установите пароль
        db.session.add(new_user)
        db.session.commit()

# Маршрут для получения токена
@app.route('/token', methods=['POST'])
def get_token():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.username, expires_delta=timedelta(minutes=30))
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Неверные учетные данные"}), 401

# Защищенный маршрут для получения информации о бонусах
@app.route('/bonus', methods=['GET'])
@jwt_required()
def read_bonus_data():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if user:
        bonus_level, min_spending, max_spending = determine_bonus_level(user.spending)

        return {
            "bonus_level": bonus_level,
            "current_spending": user.spending,
            "min_spending": min_spending,
            "max_spending": max_spending
        }, 200
    else:
        return {"msg": "Пользователь не найден"}, 404

# Маршрут для добавления нового пользователя (только для администраторов)
@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.json.get('username')
    password = request.json.get('password')
    spending = request.json.get('spending', 0.0)  # Уровень трат, по умолчанию 0.0

    if User.query.filter_by(username=username).first():
        return {"msg": "Пользователь уже существует"}, 400

    new_user = User(username=username)
    new_user.set_password(password)
    new_user.spending = spending  # Установка уровня трат
    db.session.add(new_user)
    db.session.commit()

    return {"msg": "Пользователь создан"}, 201

@app.route('/users', methods=['GET'])
@jwt_required()  # Защита маршрута, чтобы доступ был только для авторизованных пользователей
def get_users():
    users = User.query.all()  # Получаем всех пользователей из базы данных

    # Формируем список пользователей
    users_list = []
    for user in users:
        users_list.append({
            'id': user.id,
            'username': user.username,
            'spending': user.spending
        })

    return jsonify(users_list), 200  # Возвращаем список пользователей и статус 200

@app.route('/users/<int:id>/transactions', methods=['POST'])
@jwt_required()  # Защита маршрута, чтобы доступ был только для авторизованных пользователей
def add_transaction(id):
    current_user = get_jwt_identity()
    user = User.query.get(id)

    if user is None:
        return {"msg": "Пользователь не найден"}, 404

    # Проверяем, имеет ли текущий пользователь права на добавление транзакции
    if user.username != current_user:
        return {"msg": "У вас нет прав для добавления транзакций этому пользователю"}, 403

    # Получаем сумму транзакции из запроса
    amount = request.json.get('amount')

    if amount is None or amount <= 0:
        return {"msg": "Некорректная сумма транзакции"}, 400

    # Обновляем сумму трат пользователя
    user.spending += amount  # Предполагаем, что у вас есть поле spending в модели User
    db.session.commit()

    # Обновление уровня бонусов
    bonus_level, min_spending, max_spending = determine_bonus_level(user.spending)

    return {
        "msg": "Транзакция добавлена",
        "new_spending": user.spending,
        "bonus_level": bonus_level
    }, 201

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
