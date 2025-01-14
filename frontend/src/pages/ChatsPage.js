import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles.css'; // Подключаем CSS файл

function ChatsPage() {
    const [chats, setChats] = useState([]);
    const [users, setUsers] = useState([]);
    const [recipientId, setRecipientId] = useState('');
    const navigate = useNavigate();
    const userId = localStorage.getItem('user_id');

    useEffect(() => {
        const fetchChats = async () => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/chats`, {
                    params: { user_id: userId },
                });
                setChats(response.data);
            } catch (error) {
                console.error('Error fetching chats:', error);
            }
        };

        const fetchUsers = async () => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/users`);
                setUsers(response.data.filter((user) => user.id !== userId));
            } catch (error) {
                console.error('Error fetching users:', error);
            }
        };

        fetchChats();
        fetchUsers();
    }, [userId]);

    const startNewChat = async () => {
        if (recipientId) {
            try {
                const response = await axios.post(`${process.env.REACT_APP_API_URL}/api/chats`, {
                    user_id: userId,
                    recipient_id: recipientId,
                });
                if (response.data) {
                    alert('Chat created!');
                    setChats([...chats, response.data]);
                }
            } catch (error) {
                console.error('Error creating chat:', error);
            }
        } else {
            alert('Please select a user to start a chat.');
        }
    };

    return (
        <div className="chats-container">
            <h1 className="chats-header">Your Chats</h1>
            <div className="chat-form">
                <select
                    id="user-select"
                    value={recipientId}
                    onChange={(e) => setRecipientId(e.target.value)}
                >
                    <option value="">Select a user</option>
                    {users.map((user) => (
                        <option key={user.id} value={user.id}>
                            {user.username}
                        </option>
                    ))}
                </select>
                <button onClick={startNewChat}>Start Chat</button>
            </div>
            <ul className="chat-list">
                {chats.map((chat) => (
                    <li
                        key={chat.chat_id}
                        className="chat-item"
                        onClick={() => navigate(`/chat/${chat.chat_id}`)}
                    >
                        <p>
                            Chat with{' '}
                            {chat.participants
                                .filter((participant) => participant.id !== userId)
                                .map((participant) => participant.username)
                                .join(', ')}
                        </p>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default ChatsPage;
