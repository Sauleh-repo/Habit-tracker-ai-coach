import React, { useState } from 'react';
import { analyzeHabits, askChatbot } from '../services/api';

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [analysis, setAnalysis] = useState('');

    const handleAnalyze = async () => {
        setLoading(true);
        try {
            const response = await analyzeHabits();
            setAnalysis(response.data.reply);
        } catch (error) {
            console.error("Analysis failed", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { text: input, sender: 'user' };
        setMessages([...messages, userMessage]);
        const currentInput = input;
        setInput('');
        setLoading(true);

        try {
            const response = await askChatbot(currentInput);
            const aiMessage = { text: response.data.reply, sender: 'ai' };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            setMessages(prev => [...prev, { text: "Error connecting to AI.", sender: 'ai' }]);
        } finally {
            setLoading(false);
        }
    };

// Inside Chatbot.js return statement
    return (
        <div className="chatbot-section">
            {/* HABIT ANALYZER */}
            <article>
                <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{fontSize: '1.2rem'}}>🧠 AI Habit Coach</strong>
                    <button onClick={handleAnalyze} disabled={loading} style={{margin: 0}}>
                        {loading ? 'Analyzing...' : 'Analyze My Progress'}
                    </button>
                </header>
                {analysis ? (
                    <p className="analysis-text">{analysis}</p>
                ) : (
                    <p><small>Get a personalized review of your current habits.</small></p>
                )}
            </article>

            {/* KNOWLEDGE CHATBOT */}
            <article>
                <header><strong>💬 Ask a Wellness Question</strong></header>
                <div className="chat-window">
                    {messages.length === 0 && <p style={{textAlign: 'center', opacity: 0.5, marginTop: '15%'}}>Ask about nutrition, sleep, or exercise tips...</p>}
                    {messages.map((msg, i) => (
                        <div key={i} className={`chat-msg ${msg.sender}`}>
                            <small><strong>{msg.sender === 'user' ? 'You' : 'AI'}:</strong></small>
                            <div style={{marginTop: '4px'}}>{msg.text}</div>
                        </div>
                    ))}
                </div>
                <form onSubmit={handleSend} style={{ display: 'flex', gap: '10px', marginBottom: 0 }}>
                    <input 
                        type="text" 
                        placeholder="Type a question..." 
                        value={input} 
                        onChange={(e) => setInput(e.target.value)}
                        style={{ marginBottom: 0 }}
                    />
                    <button type="submit" style={{ width: 'auto', marginBottom: 0 }}>Ask</button>
                </form>
            </article>
        </div>
    );
};

export default Chatbot;