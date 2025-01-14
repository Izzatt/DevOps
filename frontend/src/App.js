import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ChatsPage from './pages/ChatsPage';
import ChatPage from './pages/ChatPage';
import AuthPage from './pages/AuthPage';

function App() {
    const handleLoginSuccess = (userId) => {
        localStorage.setItem('user_id', userId);
        console.log('User logged in:', userId);
    };

    return (
        <Router>
            <Routes>

                <Route path="/" element={<Navigate to="/login" />} />

                <Route path="/login" element={<AuthPage onLoginSuccess={handleLoginSuccess} />} />

                <Route path="/register" element={<RegisterPage />} />

                <Route path="/chats" element={<ChatsPage />} />

                <Route path="/chat/:chatId" element={<ChatPage />} />
            </Routes>
        </Router>
    );
}

export default App;
