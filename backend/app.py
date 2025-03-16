from gevent import monkey  # noqa: E402
monkey.patch_all()  # noqa: E402
import pytest
import json
from bson import ObjectId
from pymongo import MongoClient
from app import app  # Предполагается, что app и коллекции доступны из app.py
import os

@pytest.fixture(scope='module')
def setup_db():
    # Чтение переменной окружения для MongoDB Atlas URI
    MONGO_URI = os.getenv('MONGO_URI')
    if not MONGO_URI:
        raise ValueError("MONGO_URI is not set")
    client = MongoClient(MONGO_URI)
    db = client['test_db']
    users_collection = db['users']
    chats_collection = db['chats']

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # Тайм-аут на подключение
        client.server_info()  # Пробуем получить информацию о сервере, чтобы убедиться в успешном подключении
    except Exception as e:
        raise ValueError(f"Failed to connect to MongoDB: {e}")

    # Очистка коллекций перед каждым тестом
    users_collection.delete_many({})
    chats_collection.delete_many({})

    yield client, db, users_collection, chats_collection

    # Закрытие подключения после завершения всех тестов
    client.close()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register(client, setup_db):
    _, _, users_collection, _ = setup_db
    response = client.post('/api/users/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'User registered successfully!' in data['message']

def test_login(client, setup_db):
    _, _, users_collection, _ = setup_db
    client.post('/api/users/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.post('/api/users/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Login successful!' in data['message']

def test_get_chats(client, setup_db):
    _, _, users_collection, chats_collection = setup_db

    client.post('/api/users/register', json={
        'username': 'testuser1',
        'password': 'testpassword'
    })
    client.post('/api/users/register', json={
        'username': 'testuser2',
        'password': 'testpassword'
    })

    login_response = client.post('/api/users/login', json={
        'username': 'testuser1',
        'password': 'testpassword'
    })
    user_id = json.loads(login_response.data)['user_id']

    recipient_id = str(ObjectId())
    users_collection.insert_one({'_id': ObjectId(recipient_id), 'username': 'testuser2', 'password': 'testpassword'})
    chat_response = client.post('/api/chats', json={
        'user_id': user_id,
        'recipient_id': recipient_id
    })
    chat_id = json.loads(chat_response.data)['chat_id']

    response = client.get(f'/api/chats?user_id={user_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]['chat_id'] == chat_id