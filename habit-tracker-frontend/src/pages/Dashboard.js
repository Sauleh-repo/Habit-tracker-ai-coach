import React, { useState, useEffect } from 'react';
// --- 1. IMPORT THE NEW updateHabit FUNCTION ---
import { getHabits, toggleHabitCompletion, deleteHabit, updateHabit } from '../services/api';
import AddHabitForm from '../components/AddHabitForm';
import HabitItem from '../components/HabitItem';
// --- 2. IMPORT THE NEW MODAL COMPONENT ---
import EditHabitModal from '../components/EditHabitModal';
import './Dashboard.css';

const Dashboard = ({ token, setToken }) => {
    const [habits, setHabits] = useState([]);
    // --- 3. ADD NEW STATE TO MANAGE THE EDIT MODAL ---
    // This will hold the habit object that the user wants to edit.
    // It's `null` when the modal is closed.
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
        } else {
            setHabits([]);
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
    
    // --- 4. ADD THE HANDLER FOR SAVING AN EDITED HABIT ---
    const handleEditHabit = async (habitId, habitData) => {
        try {
            const response = await updateHabit(habitId, habitData);
            const updatedHabit = response.data;
            // Update the state to reflect the changes in the UI
            setHabits(habits.map(h => (h.id === updatedHabit.id ? updatedHabit : h)));
            // Close the modal after a successful save
            setEditingHabit(null);
        } catch (error) {
            console.error('Failed to update habit', error);
        }
    };

    return (
        <div>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2>Dashboard</h2>
                <button className="secondary" onClick={handleLogout}>Logout</button>
            </header>
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
                            // --- 5. PASS A FUNCTION TO OPEN THE MODAL ---
                            onEdit={() => setEditingHabit(habit)}
                        />
                    ))}
                </div>
            ) : (
                <p>You haven't added any habits yet. Add one above to get started!</p>
            )}

            {/* --- 6. RENDER THE MODAL --- */}
            {/* The modal is always in the DOM, but it's only visible when `editingHabit` is not null */}
            <EditHabitModal
                habit={editingHabit}
                onSave={handleEditHabit}
                onClose={() => setEditingHabit(null)}
            />
        </div>
    );
};

export default Dashboard;