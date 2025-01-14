from gevent import monkey
monkey.patch_all()
from flask import Flask, request, jsonify, Response
from prometheus_client import Counter, Histogram, generate_latest
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from bson import ObjectId
from pymongo.mongo_client import MongoClient
import time
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
CORS(app, resources={r"/*": {"origins": "*"}})

socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB setup
uri = os.getenv('MONGO_URI')
client = MongoClient(uri)
db = client['chat_app']
users_collection = db['users']
chats_collection = db['chats']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'api_request_count', 'Total API Requests', ['method', 'endpoint', 'status_code']
)
REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds', 'Latency of API Requests', ['method', 'endpoint']
)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request(response):
    latency = time.time() - request.start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status_code=response.status_code).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(latency)
    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), content_type='text/plain')

# User registration
@app.route('/api/users/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({'username': username, 'password': hashed_password})
    return jsonify({'message': 'User registered successfully!'})

# User login
@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        return jsonify({'message': 'Login successful!', 'user_id': str(user["_id"])})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/chats', methods=['GET'])
def get_chats():
    user_id = request.args.get('user_id')
    chats = chats_collection.find({'participants': user_id})

    chat_list = []
    for chat in chats:
        participants_info = [
            {
                'id': str(participant_id),
                'username': users_collection.find_one({'_id': ObjectId(participant_id)})['username']
            }
            for participant_id in chat['participants']
        ]
        chat_list.append({
            'chat_id': str(chat['_id']),
            'participants': participants_info
        })
    return jsonify(chat_list)

# Fetch users
@app.route('/api/users', methods=['GET'])
def get_users():
    users = users_collection.find({}, {'_id': 1, 'username': 1})
    return jsonify([{'id': str(user['_id']), 'username': user['username']} for user in users])

# Start a new chat
@app.route('/api/chats', methods=['POST'])
def start_chat():
    data = request.json
    user_id = data.get('user_id')
    recipient_id = data.get('recipient_id')

    if not users_collection.find_one({'_id': ObjectId(user_id)}) or \
       not users_collection.find_one({'_id': ObjectId(recipient_id)}):
        return jsonify({'error': 'User(s) not found'}), 400

    chat = {
        'participants': [user_id, recipient_id],
        'messages': []
    }
    result = chats_collection.insert_one(chat)
    return jsonify({'chat_id': str(result.inserted_id)})

# Send message
@app.route('/api/chats/<chat_id>/message', methods=['POST'])
def send_message(chat_id):
    data = request.json
    sender_id = data.get('sender_id')
    message = data.get('message')

    if not sender_id or not message:
        return jsonify({'error': 'Missing sender_id or message'}), 400

    chats_collection.update_one(
        {'_id': ObjectId(chat_id)},
        {'$push': {'messages': {'sender_id': sender_id, 'content': message}}}
    )

    return jsonify({'message': 'Message sent successfully!'})

@app.route('/api/chats/<chat_id>/participants', methods=['GET'])
def get_chat_participants(chat_id):
    try:
        chat = chats_collection.find_one({'_id': ObjectId(chat_id)})
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404

        participants = []
        for participant_id in chat['participants']:
            user = users_collection.find_one({'_id': ObjectId(participant_id)}, {'_id': 1, 'username': 1})
            if user:
                participants.append({'id': str(user['_id']), 'username': user['username']})

        return jsonify(participants)
    except Exception as e:
        print(f"Error fetching participants for chat {chat_id}: {e}")
        return jsonify({'error': 'Failed to fetch participants'}), 500


# Fetch messages from a chat
@app.route('/api/chats/<chat_id>', methods=['GET'])
def fetch_messages(chat_id):
    try:
        chat = chats_collection.find_one({'_id': ObjectId(chat_id)})
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404

        messages_with_usernames = []
        for message in chat.get('messages', []):
            sender = users_collection.find_one({'_id': ObjectId(message['sender_id'])})
            messages_with_usernames.append({
                'sender_username': sender['username'] if sender else 'Unknown',
                'content': message['content']
            })

        return jsonify(messages_with_usernames)
    except Exception as e:
        print(f"Error fetching messages for chat_id {chat_id}: {e}")
        return jsonify({'error': 'Invalid chat ID format'}), 400


# WebSocket real-time chat
@socketio.on('join')
def on_join(data):
    join_room(data['chat_id'])

@socketio.on('message')
def handle_message(data):
    chat_id = data.get('chat_id')
    message = data.get('message')
    sender_id = data.get('sender_id')

    if chat_id and message and sender_id:
        chats_collection.update_one(
            {'_id': ObjectId(chat_id)},
            {'$push': {'messages': {'sender_id': sender_id, 'content': message}}}
        )
        emit('message', {'chat_id': chat_id, 'sender_id': sender_id, 'message': message}, room=chat_id)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)