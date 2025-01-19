from gevent import monkey  
monkey.patch_all()
import pytest
import json
from bson import ObjectId
from pymongo import MongoClient
from app import app, users_collection, chats_collection  # Предполагается, что app и коллекции доступны из app.py

# Настройка подключения к MongoDB Atlas
MONGO_URI = 'mongodb+srv://izzat:dbpa$$word1234@cluster0.cvhz3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(MONGO_URI)
db = client['chat_app']
users_collection = db['users']
chats_collection = db['chats']

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def cleanup():
    # Очистка коллекций перед каждым тестом
    users_collection.delete_many({})
    chats_collection.delete_many({})

def test_register(client):
    response = client.post('/api/users/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'User registered successfully!' in data['message']

def test_login(client):
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

def test_get_chats(client):
    # Регистрация пользователей
    client.post('/api/users/register', json={
        'username': 'testuser1',
        'password': 'testpassword'
    })
    client.post('/api/users/register', json={
        'username': 'testuser2',
        'password': 'testpassword'
    })

    # Логин и получение user_id
    login_response = client.post('/api/users/login', json={
        'username': 'testuser1',
        'password': 'testpassword'
    })
    user_id = json.loads(login_response.data)['user_id']

    # Создание чата с валидными ObjectId
    recipient_id = str(ObjectId())
    users_collection.insert_one({'_id': ObjectId(recipient_id), 'username': 'testuser2', 'password': 'testpassword'})  # Добавление получателя в коллекцию users
    chat_response = client.post('/api/chats', json={
        'user_id': user_id,
        'recipient_id': recipient_id
    })
    chat_id = json.loads(chat_response.data)['chat_id']

    # Получение списка чатов
    response = client.get(f'/api/chats?user_id={user_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]['chat_id'] == chat_id
