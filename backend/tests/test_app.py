import json
import pytest
from app import app, users_collection, chats_collection
from bson import ObjectId
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    """Фикстура для создания тестового клиента приложения."""
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


@pytest.fixture
def user():
    """Фикстура для создания тестового пользователя."""
    user_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    hashed_password = generate_password_hash(user_data['password'])
    users_collection.insert_one({'username': user_data['username'], 'password': hashed_password})
    return user_data


@pytest.fixture
def chat(user):
    """Фикстура для создания чата для тестового пользователя."""
    user_id = str(users_collection.find_one({'username': user['username']})['_id'])
    recipient_id = user_id  # Для простоты используем того же пользователя как собеседника
    chat = {'participants': [user_id, recipient_id], 'messages': []}
    chat_id = chats_collection.insert_one(chat).inserted_id
    return str(chat_id)


def test_register(client):
    """Тестирование маршрута регистрации."""
    data = {
        'username': 'newuser',
        'password': 'newpassword'
    }
    response = client.post('/api/users/register', json=data)
    assert response.status_code == 200
    assert b'User registered successfully!' in response.data


def test_register_existing_user(client, user):
    """Тестирование регистрации с уже существующим пользователем."""
    data = {
        'username': user['username'],
        'password': 'somepassword'
    }
    response = client.post('/api/users/register', json=data)
    assert response.status_code == 400
    assert b'Username already exists' in response.data


def test_login(client, user):
    """Тестирование маршрута авторизации."""
    data = {
        'username': user['username'],
        'password': user['password']
    }
    response = client.post('/api/users/login', json=data)
    assert response.status_code == 200
    assert b'Login successful!' in response.data


def test_login_invalid_credentials(client):
    """Тестирование авторизации с неверными данными."""
    data = {
        'username': 'invaliduser',
        'password': 'wrongpassword'
    }
    response = client.post('/api/users/login', json=data)
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data


def test_get_chats(client, user, chat):
    """Тестирование маршрута получения чатов пользователя."""
    data = {'user_id': str(users_collection.find_one({'username': user['username']})['_id'])}
    response = client.get('/api/chats', query_string=data)
    assert response.status_code == 200
    assert len(json.loads(response.data)) > 0


def test_start_chat(client, user):
    """Тестирование маршрута создания нового чата."""
    data = {
        'user_id': str(users_collection.find_one({'username': user['username']})['_id']),
        'recipient_id': str(users_collection.find_one({'username': user['username']})['_id'])  # Используем того же пользователя
    }
    response = client.post('/api/chats', json=data)
    assert response.status_code == 200
    chat_id = json.loads(response.data).get('chat_id')
    assert chat_id is not None
    assert isinstance(chat_id, str)


def test_send_message(client, chat, user):
    """Тестирование маршрута отправки сообщения в чат."""
    data = {
        'sender_id': str(users_collection.find_one({'username': user['username']})['_id']),
        'message': 'Hello, this is a test message!'
    }
    response = client.post(f'/api/chats/{chat}/message', json=data)
    assert response.status_code == 200
    assert b'Message sent successfully!' in response.data


def test_get_chat_participants(client, chat):
    """Тестирование маршрута получения участников чата."""
    response = client.get(f'/api/chats/{chat}/participants')
    assert response.status_code == 200
    participants = json.loads(response.data)
    assert isinstance(participants, list)
    assert len(participants) > 0
