import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles.css';
import PropTypes from 'prop-types';

function LoginPage({ navigateToRegister }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate(); 

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(`${process.env.REACT_APP_API_URL}/api/users/login`, {
                username,
                password,
            });

            alert(response.data.message);
            localStorage.setItem('user_id', response.data.user_id);


            navigate('/chats');
        } catch (error) {
            console.error('Login error:', error.response || error);
            alert(error.response?.data?.error || 'Login failed');
        }
    };

    return (
        <div className="auth-container">
            <form className="auth-form" onSubmit={handleLogin}>
                <h2>Login</h2>
                <label htmlFor="username">Username</label>
                <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username"
                    required
                />
                <label htmlFor="password">Password</label>
                <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                />
                <button type="submit">Login</button>
                <div className="form-footer">
                    Don&apos;t have an account?{' '}
                    <a
                        href="#"
                        onClick={(e) => {
                            e.preventDefault();
                            navigateToRegister();
                        }}
                    >
                        Register
                    </a>
                </div>
            </form>
        </div>
    );
}

LoginPage.propTypes = {
    navigateToRegister: PropTypes.func.isRequired, // Обязательно указываем тип и что это поле обязательно
};

export default LoginPage;
