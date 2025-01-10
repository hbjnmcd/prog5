import pytest
from app import app, db, User
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Используем in-memory базу данных для тестов
    with app.app_context():
        db.create_all()  # Создаем таблицы
        yield app.test_client()  # Возвращаем клиент для тестирования
        db.drop_all()  # Удаляем таблицы после тестов

@pytest.fixture
def test_user(client):
    user = User(username='testuser')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

def test_get_token(client, test_user):
    response = client.post('/token', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.get_json()

def test_get_token_invalid_credentials(client):
    response = client.post('/token', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.get_json() == {"msg": "Неверные учетные данные"}

def test_read_bonus_data(client, test_user):
    access_token = create_access_token(identity=test_user.username)
    response = client.get('/bonus', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'bonus_level' in data
    assert 'current_spending' in data

def test_add_user(client):
    response = client.post('/add_user', json={
        'username': 'newuser',
        'password': 'newpassword',
        'spending': 150.0
    })
    assert response.status_code == 201
    assert response.get_json() == {"msg": "Пользователь создан"}

def test_add_user_existing(client, test_user):
    response = client.post('/add_user', json={
        'username': 'testuser',
        'password': 'newpassword'
    })
    assert response.status_code == 400
    assert response.get_json() == {"msg": "Пользователь уже существует"}

def test_add_transaction(client, test_user):
    access_token = create_access_token(identity=test_user.username)
    response = client.post(f'/users/{test_user.id}/transactions', json={
        'amount': 100.0
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 201
    assert response.get_json()['msg'] == "Транзакция добавлена"

def test_add_transaction_invalid_user(client, test_user):
    access_token = create_access_token(identity=test_user.username)
    response = client.post('/users/999/transactions', json={
        'amount': 100.0
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 404
    assert response.get_json() == {"msg": "Пользователь не найден"}

def test_add_transaction_no_permission(client, test_user):
    other_user = User(username='otheruser')
    other_user.set_password('password123')
    db.session.add(other_user)
    db.session.commit()

    access_token = create_access_token(identity='otheruser')
    response = client.post(f'/users/{test_user.id}/transactions', json={
        'amount': 100.0
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 403
    assert response.get_json() == {"msg": "У вас нет прав для добавления транзакций этому пользователю"}

def test_add_transaction_invalid_amount(client, test_user):
    access_token = create_access_token(identity=test_user.username)
    response = client.post(f'/users/{test_user.id}/transactions', json={
        'amount': -50.0
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 400
    assert response.get_json() == {"msg": "Некорректная сумма транзакции"}