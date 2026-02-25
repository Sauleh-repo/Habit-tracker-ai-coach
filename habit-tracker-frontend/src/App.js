import React, { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import RegisterPage from './pages/RegisterPage';
import './App.css';

function App() {
  const [token, setToken] = useState(null);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) setToken(storedToken);
  }, []);

  return (
    <main>
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