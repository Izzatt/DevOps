import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import io from 'socket.io-client';
import axios from 'axios';
import '../styles.css';

const socket = io('backend.default.svc.cluster.local:5000/socket.io/');


function ChatPage() {
    const { chatId } = useParams(); 
    const [messages, setMessages] = useState([]); 
    const [message, setMessage] = useState('');
    const [usernames, setUsernames] = useState({}); 
    const userId = localStorage.getItem('user_id'); 
    const messagesEndRef = useRef(null); 


    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };


    useEffect(() => {
        const fetchChatData = async () => {
            try {

                const messagesResponse = await axios.get(`${process.env.REACT_APP_API_URL}/api/chats/${chatId}`);
                setMessages(messagesResponse.data);


                const participantsResponse = await axios.get(`${process.env.REACT_APP_API_URL}/api/chats/${chatId}/participants`);
                const usernamesMap = participantsResponse.data.reduce((acc, user) => {
                    acc[user.id] = user.username;
                    return acc;
                }, {});
                setUsernames(usernamesMap);
            } catch (error) {
                console.error('Error fetching chat data:', error.response || error);
            }
        };

        fetchChatData();
    }, [chatId]);


    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        socket.emit('join', { chat_id: chatId });

        socket.on('message', (data) => {
            if (data.chat_id === chatId) {
                setMessages((prev) => [...prev, data]); 
            }
        });

        return () => {
            socket.off('message');
            socket.emit('leave', { chat_id: chatId });
        };
    }, [chatId]);

    const sendMessage = async () => {
        if (message.trim()) {
            const newMessage = {
                chat_id: chatId,
                sender_id: userId,
                message: message.trim(),
            };

            try {
                socket.emit('message', newMessage); 
                await axios.post(`${process.env.REACT_APP_API_URL}/api/chats/${chatId}/message`, newMessage); 
                setMessage(''); 
            } catch (error) {
                console.error('Error sending message:', error.response || error);
            }
        } else {
            alert('Message cannot be empty!');
        }
    };

    return (
        <div className="chat-container">
            <h1>Chat Room</h1>
            <div className="messages-container">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`message ${msg.sender_id === userId ? 'message-right' : 'message-left'}`}
                    >
                        <p className="message-username">
                            {msg.sender_id === userId ? 'You' : usernames[msg.sender_id] || 'Unknown'}:
                        </p>
                        <p className="message-content">{msg.message || msg.content}</p>
                    </div>
                ))}
                <div ref={messagesEndRef} /> {}
            </div>
            <div className="input-container">
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type a message..."
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
}

export default ChatPage;
