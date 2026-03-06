import React, { useState, useEffect } from "react";
// Use HashRouter - it is the most reliable for Cloud Storage
import {
  HashRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Toaster } from "react-hot-toast";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import Dashboard from "./pages/Dashboard";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (storedToken) setToken(storedToken);
  }, []);

  return (
    <Router>
      {/* 1. Move Toaster inside the main flow to avoid 'animation' errors */}
      <Toaster position="top-right" />

      <div className="container">
        <Routes>
          <Route
            path="/login"
            element={
              !token ? <LoginPage setToken={setToken} /> : <Navigate to="/" />
            }
          />
          <Route
            path="/register"
            element={!token ? <RegisterPage /> : <Navigate to="/" />}
          />
          <Route
            path="/"
            element={
              token ? (
                <Dashboard token={token} setToken={setToken} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />

          {/* 2. THE CRITICAL ADDITION: Redirect 'index.html' to the root */}
          <Route path="/index.html" element={<Navigate to="/" />} />

          {/* 3. Catch-all: If anything else matches (like bucket paths), go home */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
