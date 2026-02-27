import React, { useState } from 'react';
import { register } from '../services/api';
import { Link } from 'react-router-dom'; // Import Link

const RegisterPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [isError, setIsError] = useState(false);

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            await register(username, password);
            setMessage('Registration successful! You can now log in.');
            setIsError(false);
        } catch (error) {
            setMessage('Registration failed. Username may already be taken.');
            setIsError(true);
        }
    };

    return (
        <article style={{ maxWidth: '400px', margin: '2rem auto' }}>
            <header>
                <h2 style={{ margin: 0 }}>Register</h2>
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
            {message && (
                <p style={{ color: isError ? 'red' : 'green' }}>{message}</p>
            )}

            {/* --- ADD THIS NAVIGATION LINK --- */}
            <footer>
                <p style={{ margin: 0, textAlign: 'center' }}>
                    Already have an account? <Link to="/login">Login here</Link>
                </p>
            </footer>
        </article>
    );
};

export default RegisterPage;