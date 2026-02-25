import React, { useState } from 'react';
import { createHabit } from '../services/api';

const AddHabitForm = ({ onHabitAdded }) => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // We pass a SINGLE object here
            const response = await createHabit({ name, description }); 
            onHabitAdded(response.data);
            setName('');
            setDescription('');
        } catch (error) {
            console.error('Failed to create habit', error);
        }
    };

    return (
        // 1. Wrap the form in an <article> tag for the card styling.
        <article>
            {/* 2. Add a <header> for better structure and consistency. */}
            <header>
                <h3>Add a New Habit</h3>
            </header>

            {/* The form itself remains the same. Pico will style its elements. */}
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Habit Name (e.g., Drink Water)"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                />
                <input
                    type="text"
                    placeholder="Description (e.g., 8 glasses a day)"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                />
                <button type="submit">Add Habit</button>
            </form>
        </article>
    );
};

export default AddHabitForm;