import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000', 
});

// Interceptor to attach the JWT Token to every request
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Interceptor to handle expired tokens
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token');
            window.location.reload();
        }
        return Promise.reject(error);
    }
);

// --- Auth Functions ---
export const register = (username, password) => {
    return apiClient.post('/users/register', { username, password });
};

export const login = (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return apiClient.post('/token', formData);
};

// --- Habit Functions ---
export const getHabits = () => {
    return apiClient.get('/habits/');
};

// Standardized to accept a single object: { name: "...", description: "..." }
export const createHabit = (habitData) => {
    return apiClient.post('/habits/', habitData);
};

export const toggleHabitCompletion = (habitId) => {
    return apiClient.put(`/habits/${habitId}/toggle`);
};

export const deleteHabit = (habitId) => {
    return apiClient.delete(`/habits/${habitId}`);
};

// Standardized to accept a single object for updates
export const updateHabit = (habitId, habitData) => {
    return apiClient.put(`/habits/${habitId}`, habitData);
};

// --- AI Chatbot Functions ---
export const analyzeHabits = () => {
    return apiClient.post('/chatbot/analyze');
};

export const askChatbot = (message) => {
    return apiClient.post('/chatbot/ask', { message });
};