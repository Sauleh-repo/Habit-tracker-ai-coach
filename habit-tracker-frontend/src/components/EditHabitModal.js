import React, { useState, useEffect } from 'react';
import './EditHabitModal.css';

const EditHabitModal = ({ habit, onSave, onClose }) => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');

    useEffect(() => {
        if (habit) {
            setName(habit.name);
            setDescription(habit.description || '');
        }
    }, [habit]);

    const handleSave = (e) => {
        e.preventDefault();
        onSave(habit.id, { name, description });
    };

    if (!habit) {
        return null;
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <article>
                    <header>
                        <h2>Edit Habit</h2>
                        <button aria-label="Close" className="close" onClick={onClose}></button>
                    </header>
                    <form onSubmit={handleSave}>
                        <label htmlFor="name">Habit Name</label>
                        <input
                            type="text"
                            id="name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                        />

                        <label htmlFor="description">Description</label>
                        <input
                            type="text"
                            id="description"
                            placeholder="Optional description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                        />

                        <footer>
                            <button type="button" className="secondary" onClick={onClose}>
                                Cancel
                            </button>
                            <button type="submit">Save Changes</button>
                        </footer>
                    </form>
                </article>
            </div>
        </div>
    );
};

export default EditHabitModal;