import React, { useState, useEffect } from 'react';
import { analyzeHabits, askChatbot, getChatHistory } from '../services/api';

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [analysis, setAnalysis] = useState('');

    useEffect(() => {
        const loadHistory = async () => {
            try {
                const response = await getChatHistory();
                const formattedHistory = response.data.map(msg => ({
                    text: msg.content,
                    sender: msg.role === 'user' ? 'user' : 'ai'
                }));
                setMessages(formattedHistory);
            } catch (error) {
                console.error("Failed to load chat history:", error);
            }
        };
        loadHistory();
    }, []);

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

        const userMsg = { text: input, sender: 'user' };
        setMessages(prev => [...prev, userMsg]);
        
        const currentInput = input;
        setInput('');
        setLoading(true);

        try {
            const response = await askChatbot(currentInput);
            const aiMsg = { text: response.data.reply, sender: 'ai' };
            setMessages(prev => [...prev, aiMsg]);
        } catch (error) {
            setMessages(prev => [...prev, { text: "Error connecting to AI.", sender: 'ai' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chatbot-section">
            <article>
                <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{fontSize: '1.2rem'}}>🧠 AI Habit Coach</strong>
                    <button onClick={handleAnalyze} disabled={loading} style={{margin: 0}}>
                        {loading ? 'Analyzing...' : 'Analyze My Progress'}
                    </button>
                </header>
                {analysis ? (
                    <p className="analysis-text" style={{ lineHeight: '1.6', color: '#60a5fa' }}>{analysis}</p>
                ) : (
                    <p><small>Get a personalized review of your current habits.</small></p>
                )}
            </article>

            <article>
                <header><strong>💬 Ask a Wellness Question</strong></header>
                <div className="chat-window" style={{ height: '300px', overflowY: 'auto', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {messages.length === 0 && <p style={{textAlign: 'center', opacity: 0.5, marginTop: '15%'}}>Ask about nutrition, sleep, or exercise tips...</p>}
                    
                    {messages.map((msg, i) => (
                        <div key={i} className={`chat-msg ${msg.sender}`} style={{
                            padding: '0.5rem 1rem',
                            borderRadius: '8px',
                            width: '90%',
                            background: msg.sender === 'user' ? 'rgba(37, 99, 235, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                            borderLeft: msg.sender === 'user' ? '3px solid #2563eb' : '3px solid #94a3b8'
                        }}>
                            <small><strong>{msg.sender === 'user' ? 'You' : 'AI'}:</strong></small>
                            <div style={{marginTop: '4px'}}>{msg.text}</div>
                        </div>
                    ))}
                    {loading && <p style={{fontSize: '0.8rem', opacity: 0.7}}>AI is thinking...</p>}
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