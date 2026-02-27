import React from 'react';

const HabitItem = ({ habit, onToggle, onDelete, onEdit }) => {
    
    const isToday = (someDate) => {
        if (!someDate) return false;
        const today = new Date();
        const date = new Date(someDate + 'T00:00:00');
        return date.getFullYear() === today.getFullYear() &&
               date.getMonth() === today.getMonth() &&
               date.getDate() === today.getDate();
    };

    const isCompleted = isToday(habit.last_completed_at);

    return (
        <article className="habit-item">
            <div className="habit-content">
                <label>
                    <input
                        type="checkbox"
                        checked={isCompleted}
                        onChange={() => onToggle(habit.id)}
                    />
                    <span className={isCompleted ? 'completed' : ''}>
                        <strong>{habit.name}</strong>
                        {habit.description && `: ${habit.description}`}
                    </span>
                </label>
            </div>
            <div className="habit-actions">
                <button 
                    className="secondary outline"
                    onClick={() => onEdit(habit)}
                >
                    Edit
                </button>
                
                <button 
                    className="secondary outline" 
                    onClick={() => onDelete(habit.id)}
                >
                    Delete
                </button>
            </div>
        </article>
    );
};

export default HabitItem;