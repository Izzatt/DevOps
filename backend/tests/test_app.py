import pytest
from app import app, users_collection, chats_collection
from werkzeug.security import generate_password_hash
from bson import ObjectId


@pytest.fixture
def client():
    """Создает тестовый клиент Flask"""
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup_database():
    """Очистка базы данных перед каждым тестом"""
    users_collection.delete_many({})
    chats_collection.delete_many({})
    yield


def test_user_registration(client):
    response = client.post('/api/users/register', json={
        'username': 'test_user',
        'password': 'test_password'
    })
    assert response.status_code == 200
    assert response.json['message'] == 'User registered successfully!'


def test_duplicate_user_registration(client):
    users_collection.insert_one({
        'username': 'test_user',
        'password': generate_password_hash('test_password')
    })
    response = client.post('/api/users/register', json={
        'username': 'test_user',
        'password': 'test_password'
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Username already exists'


def test_user_login(client):
    hashed_password = generate_password_hash('test_password')
    users_collection.insert_one({
        'username': 'test_user',
        'password': hashed_password
    })
    response = client.post('/api/users/login', json={
        'username': 'test_user',
        'password': 'test_password'
    })
    assert response.status_code == 200
    assert 'user_id' in response.json


def test_invalid_user_login(client):
    response = client.post('/api/users/login', json={
        'username': 'non_existent_user',
        'password': 'test_password'
    })
    assert response.status_code == 401
    assert response.json['error'] == 'Invalid credentials'


def test_start_chat(client):
    user1_id = str(users_collection.insert_one({'username': 'user1', 'password': 'pass1'}).inserted_id)
    user2_id = str(users_collection.insert_one({'username': 'user2', 'password': 'pass2'}).inserted_id)

    response = client.post('/api/chats', json={
        'user_id': user1_id,
        'recipient_id': user2_id
    })
    assert response.status_code == 200
    assert 'chat_id' in response.json


def test_get_users(client):
    users_collection.insert_many([
        {'username': 'user1', 'password': 'pass1'},
        {'username': 'user2', 'password': 'pass2'}
    ])
    response = client.get('/api/users')
    assert response.status_code == 200
    assert len(response.json) == 2


def test_send_message(client):
    chat_id = str(chats_collection.insert_one({
        'participants': ['user1', 'user2'],
        'messages': []
    }).inserted_id)

    response = client.post(f'/api/chats/{chat_id}/message', json={
        'sender_id': 'user1',
        'message': 'Hello, user2!'
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Message sent successfully!'


def test_fetch_messages(client):
    chat_id = str(chats_collection.insert_one({
        'participants': ['user1', 'user2'],
        'messages': [{'sender_id': 'user1', 'content': 'Hello, user2!'}]
    }).inserted_id)

    response = client.get(f'/api/chats/{chat_id}')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['content'] == 'Hello, user2!'
