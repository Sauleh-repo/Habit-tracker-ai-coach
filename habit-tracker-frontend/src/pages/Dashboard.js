import React, { useState, useEffect } from 'react';
import { getHabits, toggleHabitCompletion, deleteHabit, updateHabit } from '../services/api';
import AddHabitForm from '../components/AddHabitForm';
import HabitItem from '../components/HabitItem';
import Chatbot from '../components/Chatbot';
import EditHabitModal from '../components/EditHabitModal';
import './Dashboard.css';

const Dashboard = ({ token, setToken }) => {
    const [habits, setHabits] = useState([]);
    const [editingHabit, setEditingHabit] = useState(null);

    useEffect(() => {
        if (token) {
            const fetchHabits = async () => {
                try {
                    const response = await getHabits();
                    setHabits(response.data);
                } catch (error) {
                    console.error('Failed to fetch habits:', error);
                }
            };
            fetchHabits();
        }
    }, [token]);

    const handleHabitAdded = (newHabit) => {
        setHabits([...habits, newHabit]);
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        setToken(null);
    };

    const handleToggleHabit = async (habitId) => {
        try {
            const response = await toggleHabitCompletion(habitId);
            const updatedHabit = response.data;
            setHabits(habits.map(h => (h.id === updatedHabit.id ? updatedHabit : h)));
        } catch (error) {
            console.error('Failed to toggle habit', error);
        }
    };
    
    const handleDeleteHabit = async (habitId) => {
        if (window.confirm('Are you sure you want to delete this habit?')) {
            try {
                await deleteHabit(habitId);
                setHabits(habits.filter(h => h.id !== habitId));
            } catch (error) {
                console.error('Failed to delete habit', error);
            }
        }
    };
    
    const handleEditHabit = async (habitId, habitData) => {
        try {
            const response = await updateHabit(habitId, habitData);
            const updatedHabit = response.data;
            setHabits(habits.map(h => (h.id === updatedHabit.id ? updatedHabit : h)));
            setEditingHabit(null);
        } catch (error) {
            console.error('Failed to update habit', error);
        }
    };

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <h2>Dashboard</h2>
                <button className="secondary outline" onClick={handleLogout}>Logout</button>
            </header>
            <hr />

            <Chatbot />
            <hr />
            
            <AddHabitForm onHabitAdded={handleHabitAdded} />

            <hr />
            <h3>Your Habits</h3>

            {habits.length > 0 ? (
                <div>
                    {habits.map((habit) => (
                        <HabitItem 
                            key={habit.id}
                            habit={habit}
                            onToggle={handleToggleHabit}
                            onDelete={handleDeleteHabit}
                            onEdit={() => setEditingHabit(habit)}
                        />
                    ))}
                </div>
            ) : (
                <p>You haven't added any habits yet. Add one above to get started!</p>
            )}

            <EditHabitModal
                habit={editingHabit}
                onSave={handleEditHabit}
                onClose={() => setEditingHabit(null)}
            />
        </div>
    );
};

export default Dashboard;