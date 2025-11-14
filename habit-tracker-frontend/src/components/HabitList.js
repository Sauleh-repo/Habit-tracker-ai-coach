useEffect(() => {
    const fetchHabits = async () => {
        try {
            const response = await getHabits(token);
            setHabits(response.data);
        } catch (error) {
            console.error('Failed to fetch habits', error);
        }
    };

    fetchHabits();
}, [token]); // Re-fetch when token changes

return (
    <div>
        <h3>Your Habits</h3>
        <ul>
            {habits.map((habit) => (
                <li key={habit.id}>
                    <strong>{habit.name}</strong>: {habit.description}
                </li>
            ))}
        </ul>
    </div>
);