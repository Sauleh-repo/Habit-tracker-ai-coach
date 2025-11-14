import React, { useState } from 'react';
import { register } from '../services/api';

const RegisterPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [isError, setIsError] = useState(false); // State to track message type

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            await register(username, password);
            setMessage('Registration successful! You can now log in.');
            setIsError(false); // It's a success message
        } catch (error) {
            setMessage('Registration failed. Username may already be taken.');
            setIsError(true); // It's an error message
            console.error(error);
        }
    };

    return (
        // 1. Replaced the <div> with an <article> tag for the card style.
        <article>
            {/* 2. Added a <header> for semantic structure. */}
            <header>
                <h2>Register</h2>
            </header>

            <form onSubmit={handleRegister}>
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
                <button type="submit">Register</button>
            </form>

            {/* 3. Conditionally style the message based on success or error. */}
            {message && (
                <p style={{ color: isError ? 'var(--pico-color-red-500)' : 'var(--pico-color-green-500)' }}>
                    {message}
                </p>
            )}
        </article>
    );
};

export default RegisterPage;