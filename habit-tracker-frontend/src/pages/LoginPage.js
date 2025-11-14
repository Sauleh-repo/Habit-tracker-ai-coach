import React, { useState } from 'react';
import { login } from '../services/api';

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
            console.error(err);
        }
    };

    return (
        // 1. Replaced the <div> with an <article> tag.
        //    Pico.css automatically styles this as a card.
        <article>
            {/* 2. Added a <header> for better semantic structure. */}
            <header>
                <h2>Login</h2>
            </header>

            {/* The form itself is unchanged. Pico styles the inputs and buttons automatically. */}
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

            {/* 3. (Optional but good practice) Use a Pico CSS variable for the error color. */}
            {error && <p style={{ color: 'var(--pico-color-red-500)' }}>{error}</p>}
        </article>
    );
};

export default LoginPage;