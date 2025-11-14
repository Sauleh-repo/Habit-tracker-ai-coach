import React, { useState, useEffect } from 'react';
import './EditHabitModal.css'; // We will create this CSS file next

const EditHabitModal = ({ habit, onSave, onClose }) => {
    // State to manage the form inputs
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');

    // This useEffect hook pre-fills the form whenever a new habit is selected for editing
    useEffect(() => {
        if (habit) {
            setName(habit.name);
            setDescription(habit.description || ''); // Handle case where description is null
        }
    }, [habit]);

    // Handler for the save button
    const handleSave = (e) => {
        e.preventDefault(); // Prevent default form submission
        // Call the onSave function passed from the Dashboard,
        // providing the habit's ID and the new details.
        onSave(habit.id, { name, description });
    };

    // If no habit is passed, the modal is hidden, so we render nothing.
    if (!habit) {
        return null;
    }

    return (
        // The modal overlay that covers the page
        <div className="modal-overlay" onClick={onClose}>
            {/* The modal content itself. We stop propagation to prevent the overlay click from closing it. */}
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <article>
                    <header>
                        <h2>Edit Habit</h2>
                        {/* A close button */}
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