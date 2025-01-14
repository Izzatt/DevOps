import React, { useState } from 'react';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';

function AuthPage({ onLoginSuccess }) {
    const [isLogin, setIsLogin] = useState(true); 

    const navigateToRegister = () => setIsLogin(false);
    const navigateToLogin = () => setIsLogin(true);

    return (
        <div className="auth-page">
            {isLogin ? (
                <LoginPage
                    navigateToRegister={navigateToRegister}
                    onLoginSuccess={onLoginSuccess}
                />
            ) : (
                <RegisterPage navigateToLogin={navigateToLogin} />
            )}
        </div>
    );
}

export default AuthPage;
