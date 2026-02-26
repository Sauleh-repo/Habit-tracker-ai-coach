import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast'; // Professional notifications
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Sync token state if localStorage changes (e.g., from another tab)
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) setToken(storedToken);
  }, []);

  return (
    <Router>
      {/* This component renders the toast notifications globally */}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#333',
            color: '#fff',
            borderRadius: '10px',
          },
        }}
      />

      <div className="container">
        <Routes>
          {/* Login Route */}
          <Route 
            path="/login" 
            element={!token ? <LoginPage setToken={setToken} /> : <Navigate to="/" />} 
          />

          {/* Register Route */}
          <Route 
            path="/register" 
            element={!token ? <RegisterPage /> : <Navigate to="/" />} 
          />

          {/* Dashboard (Protected) */}
          <Route 
            path="/" 
            element={token ? <Dashboard token={token} setToken={setToken} /> : <Navigate to="/login" />} 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;