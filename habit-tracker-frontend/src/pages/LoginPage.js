import React, { useState } from 'react';
import { login } from '../services/api';
import { Link } from 'react-router-dom';

const LoginPage = ({ setToken }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await login(username, password);
            localStorage.setItem('token', response.data.access_token);
            setToken(response.data.access_token);
        } catch (err) {
            setError('Login failed. Please check your credentials.');
        }
    };

    return (
        <article style={{ maxWidth: '400px', margin: '2rem auto' }}>
            <header>
                <h2 style={{ margin: 0 }}>Login</h2>
            </header>
            <form onSubmit={handleLogin}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit">Login</button>
            </form>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            
            <footer>
                <p style={{ margin: 0, textAlign: 'center' }}>
                    Don't have an account? <Link to="/register">Register here</Link>
                </p>
            </footer>
        </article>
    );
};

export default LoginPage;