// src/App.js

import React, { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import RegisterPage from './pages/RegisterPage';
// --- 1. IMPORT THE CSS FILE ---
import './App.css'; 

function App() {
    const [token, setToken] = useState(null);
    const [showRegister, setShowRegister] = useState(false);

    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setToken(storedToken);
        }
    }, []);

    // --- 2. WRAP EVERYTHING IN A <main> TAG WITH THE 'container' CLASS ---
    return (
        <main className="container">
            {!token ? (
                showRegister ? (
                    <>
                        <RegisterPage />
                        <button className="secondary" onClick={() => setShowRegister(false)}>
                            Already have an account? Login
                        </button>
                    </>
                ) : (
                    <>
                        <LoginPage setToken={setToken} />
                        <button className="secondary" onClick={() => setShowRegister(true)}>
                            Need an account? Register
                        </button>
                    </>
                )
            ) : (
                <Dashboard token={token} setToken={setToken} />
            )}
        </main>
    );
}

export default App;