import React, { useState } from 'react';
import { analyzeHabits } from '../services/api';
import './Chatbot.css'; // We will create this CSS file next

const Chatbot = () => {
    const [messages, setMessages] = useState([
        { sender: 'bot', text: 'Hi there! When you\'re ready, click the button below and I\'ll give you some feedback on your habits.' }
    ]);
    const [isLoading, setIsLoading] = useState(false);

    const handleAnalyzeClick = async () => {
        setIsLoading(true);
        // Add a placeholder message so the user knows something is happening
        setMessages(prev => [...prev, { sender: 'user', text: 'Analyze my habits, please!' }]);

        try {
            const response = await analyzeHabits();
            const botReply = response.data.reply;
            setMessages(prev => [...prev, { sender: 'bot', text: botReply }]);
        } catch (error) {
            console.error('Failed to get analysis:', error);
            const errorMessage = 'Sorry, I had trouble connecting to my brain. Please try again in a moment.';
            setMessages(prev => [...prev, { sender: 'bot', text: errorMessage }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <article>
            <header>
                <h3>Your AI Habit Coach</h3>
            </header>
            
            <div className="chat-window">
                {messages.map((msg, index) => (
                    <div key={index} className={`chat-message ${msg.sender}`}>
                        <p>{msg.text}</p>
                    </div>
                ))}
                {isLoading && (
                    <div className="chat-message bot">
                        <p><i>Analyzing...</i></p>
                    </div>
                )}
            </div>

            <footer>
                <button onClick={handleAnalyzeClick} disabled={isLoading} aria-busy={isLoading}>
                    {isLoading ? 'Thinking...' : 'Analyze My Habits'}
                </button>
            </footer>
        </article>
    );
};

export default Chatbot;