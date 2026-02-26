import React, { useState } from 'react';
import { createHabit } from '../services/api';
import { toast } from 'react-hot-toast';

const AddHabitForm = ({ onHabitAdded }) => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!name.trim()) return;

        setLoading(true);
        try {
            // Sends object { name, description } to the backend
            const response = await createHabit({ name, description });
            
            // Notify the parent component (Dashboard) to update the list
            onHabitAdded(response.data);
            
            // Professional feedback
            toast.success(`Habit "${name}" started!`);
            
            // Clear the form
            setName('');
            setDescription('');
        } catch (error) {
            console.error('Failed to create habit:', error);
            toast.error('Failed to add habit. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <article>
            <header>
                <h4 style={{ margin: 0 }}>✨ Add a New Habit</h4>
            </header>
            <form onSubmit={handleSubmit} style={{ marginBottom: 0 }}>
                <div className="grid">
                    <input
                        type="text"
                        placeholder="Habit Name (e.g., Drink Water)"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                        disabled={loading}
                    />
                    <input
                        type="text"
                        placeholder="Description (e.g., 2 liters per day)"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        disabled={loading}
                    />
                </div>
                <button 
                    type="submit" 
                    className="contrast" 
                    disabled={loading || !name.trim()}
                    style={{ marginTop: '1rem' }}
                >
                    {loading ? 'Saving...' : 'Add Habit to Journey'}
                </button>
            </form>
        </article>
    );
};

export default AddHabitForm;