
import React, { useState } from 'react';
import axios from 'axios';
import '../styles.css';

function RegisterPage({ navigateToLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    const handleRegister = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }

        try {
            const response = await axios.post(`${process.env.REACT_APP_API_URL}/api/users/register`, {
                username,
                password,
            });

            alert(response.data.message || 'Registration successful!');
            navigateToLogin(); 
        } catch (error) {
            console.error('Registration error:', error.response || error);
            alert(error.response?.data?.error || 'Registration failed');
        }
    };

    return (
        <div className="auth-container">
            <form className="auth-form" onSubmit={handleRegister}>
                <h2>Register</h2>
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
                <label htmlFor="confirm-password">Confirm Password</label>
                <input
                    id="confirm-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your password"
                    required
                />
                <button type="submit">Register</button>
                <div className="form-footer">
                    Already have an account?{' '}
                    <a
                        href="#"
                        onClick={(e) => {
                            e.preventDefault();
                            navigateToLogin();
                        }}
                    >
                        Login
                    </a>
                </div>
            </form>
        </div>
    );
}

export default RegisterPage;
