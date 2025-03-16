from gevent import monkey  # noqa: E402
monkey.patch_all()  # noqa: E402
import pytest
import json
from bson import ObjectId
from pymongo import MongoClient
import os
import importlib

@pytest.fixture(scope='module')
def setup_db():
    # Set TESTING environment variable
    os.environ['TESTING'] = 'true'

    # Динамический импорт app
    app_module = importlib.import_module('app')  # Импортируем app
    app = app_module.app  # Получаем объект Flask из модуля app
    client = app.test_client()
    
    # Use the test database
    test_db = client.application.config['MONGO_DB']  # Используем тестовую базу данных
    users_collection = test_db['users']
    chats_collection = test_db['chats']

    # Очистка коллекций перед каждым тестом
    users_collection.delete_many({})
    chats_collection.delete_many({})

    yield client, test_db, users_collection, chats_collection

    # Clean up after tests
    users_collection.delete_many({})
    chats_collection.delete_many({})

@pytest.fixture
def client():
    app_module = importlib.import_module('app')  # Динамически импортируем app
    app = app_module.app  # Получаем объект Flask
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
