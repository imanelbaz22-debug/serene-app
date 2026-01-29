import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { BookOpen, Send, Trash2, Sparkles, MessageCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = '/api';

export default function Journal({ onOpenChat }) {
    const [content, setContent] = useState('');
    const [status, setStatus] = useState('idle'); // idle, loading, success
    const [history, setHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false); // Default to HIDDEN
    // Removed 'mode' state - Strictly Journal now
    const chatContainerRef = useRef(null);

    const fetchHistory = async () => {
        try {
            const res = await axios.get(`${API_URL}/journal/`);
            // Reverse history to show oldest first (chronological) 
            // Also filter locally just in case backend returns chat messages:
            const journalOnly = res.data.reverse().filter(item => item.type === 'journal');
            setHistory(journalOnly);
        } catch (err) {
            console.error("Failed to fetch history", err);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    useEffect(() => {
        if (chatContainerRef.current && showHistory) {
            chatContainerRef.current.scrollTo({
                top: chatContainerRef.current.scrollHeight,
                behavior: 'smooth'
            });
        }
    }, [history, status, showHistory]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!content.trim()) return;

        setStatus('loading');

        // Optimistically add journal entry
        const tempId = Date.now();
        const optimisticEntry = {
            id: tempId,
            type: 'journal',
            content: content,
            timestamp: new Date().toISOString(),
            isOptimistic: true,
            role: 'user'
        };

        setHistory(prev => [...prev, optimisticEntry]);
        setContent('');

        try {
            const res = await axios.post(`${API_URL}/journal/`, { content });

            // After a new entry, we show the history so they can see the analysis
            setShowHistory(true);

            // Re-fetch history to get the full entry with summary
            fetchHistory();
            setStatus('success');

            // Note: We do NOT switch to chat automatically anymore. 
            // The user stays in Journal view.

        } catch (err) {
            console.error("Failed to save entry", err);
            setStatus('idle');
            setHistory(prev => prev.filter(h => h.id !== tempId));
        }
    };

    const handleDelete = async (entryId) => {
        if (!window.confirm("Delete this journal entry?")) return;

        try {
            const dbId = entryId.toString().includes('_') ? entryId.split('_')[1] : entryId;
            await axios.delete(`${API_URL}/journal/${dbId}`);
            setHistory(history.filter(h => h.id !== entryId));
        } catch (err) {
            console.error("Failed to delete entry", err);
        }
    };

    return (
        <motion.section
            className="card journal-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            style={{
                display: 'flex',
                flexDirection: 'column',
                height: showHistory ? '700px' : '450px', // Shift height based on mode
                padding: 0,
                overflow: 'hidden',
                transition: 'height 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
        >
            <div className="journal-header" style={{ padding: '1.2rem', borderBottom: '1px solid rgba(255,255,255,0.05)', marginBottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                    <div style={{ background: 'rgba(139, 92, 246, 0.2)', padding: '0.5rem', borderRadius: '12px' }}>
                        <BookOpen size={20} className="icon-title" style={{ color: '#c4b5fd' }} />
                    </div>
                    <div>
                        <h2 style={{ fontSize: '1.1rem', marginBottom: '0.2rem', color: 'white' }}>Deep Dive Journal</h2>
                        <p style={{ fontSize: '0.8rem', opacity: 0.6, margin: 0 }}>Write freely, get AI analysis.</p>
                    </div>
                </div>

                <button
                    onClick={() => setShowHistory(!showHistory)}
                    style={{
                        background: showHistory ? 'rgba(255,255,255,0.1)' : 'transparent',
                        border: '1px solid rgba(255,255,255,0.1)',
                        padding: '0.5rem 1rem',
                        borderRadius: '8px',
                        color: 'white',
                        fontSize: '0.8rem',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        transition: 'all 0.2s'
                    }}
                >
                    {showHistory ? "Hide Recent Dives" : "View Recent Dives"}
                </button>
            </div>

            <AnimatePresence>
                {showHistory && (
                    <motion.div
                        className="chat-container"
                        ref={chatContainerRef}
                        style={{ background: 'rgba(0,0,0,0.2)', flex: 1 }}
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        {history.length === 0 && (
                            <div className="empty-history" style={{ marginTop: 'auto', marginBottom: 'auto', opacity: 0.6 }}>
                                <Sparkles size={40} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                                <p>Your safe space is ready.</p>
                                <p style={{ fontSize: '0.9rem' }}>Write your first deep dive entry! 📖</p>
                            </div>
                        )}

                        {history.map((entry) => (
                            <div key={entry.id} className="journal-entry-container" style={{ marginBottom: '2rem', padding: '0 1rem' }}>
                                <motion.div
                                    className="journal-card-content"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    style={{
                                        background: 'rgba(255, 255, 255, 0.03)',
                                        borderRadius: '16px',
                                        padding: '1.5rem',
                                        border: '1px solid rgba(255,255,255,0.08)'
                                    }}
                                >
                                    <div className="journal-meta" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', opacity: 0.5, fontSize: '0.85rem' }}>
                                        <span>{new Date(entry.timestamp).toLocaleDateString()} • {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                        {!entry.isOptimistic && (
                                            <button
                                                className="btn-delete-msg"
                                                onClick={() => handleDelete(entry.id)}
                                                title="Delete Entry"
                                                style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', padding: 0 }}
                                            >
                                                <Trash2 size={14} />
                                            </button>
                                        )}
                                    </div>

                                    <div className="journal-text" style={{ fontSize: '1.05rem', lineHeight: '1.6', marginBottom: '1.5rem', color: 'rgba(255,255,255,0.95)' }}>
                                        {entry.content}
                                    </div>

                                    {/* Analysis Section */}
                                    {entry.summary && (
                                        <div className="journal-analysis" style={{
                                            background: 'rgba(139, 92, 246, 0.08)',
                                            borderRadius: '12px',
                                            padding: '1.2rem',
                                            borderLeft: '4px solid var(--accent)'
                                        }}>
                                            <div className="analysis-header" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.8rem', color: 'var(--accent)', fontWeight: '700', fontSize: '0.9rem', letterSpacing: '0.5px' }}>
                                                <Sparkles size={16} /> DEEP DIVE ANALYSIS
                                            </div>
                                            <div className="analysis-content" style={{ fontSize: '0.95rem', opacity: 0.9, lineHeight: '1.5' }}>
                                                {entry.summary}
                                            </div>

                                            <button
                                                className="talk-about-it-btn"
                                                onClick={onOpenChat} // Now opens simple floating ChatBot
                                                style={{
                                                    marginTop: '1.2rem',
                                                    width: '100%',
                                                    background: 'rgba(255,255,255,0.08)',
                                                    border: '1px solid rgba(255,255,255,0.1)',
                                                    borderRadius: '8px',
                                                    padding: '0.8rem',
                                                    color: 'white',
                                                    fontSize: '0.9rem',
                                                    cursor: 'pointer',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    gap: '0.6rem',
                                                    transition: 'all 0.2s',
                                                    fontWeight: '500'
                                                }}
                                                onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.15)'}
                                                onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.08)'}
                                            >
                                                <MessageCircle size={18} /> Discuss with Serene
                                            </button>
                                        </div>
                                    )}
                                </motion.div>
                            </div>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="journal-composer-area" style={{
                padding: '2rem',
                background: 'rgba(255,255,255,0.02)',
                borderTop: showHistory ? '1px solid rgba(255,255,255,0.05)' : 'none',
                flex: showHistory ? 'initial' : 1,
                display: 'flex',
                alignItems: 'center'
            }}>
                <form onSubmit={handleSubmit} style={{ width: '100%', position: 'relative' }}>
                    <textarea
                        placeholder="Pour your heart out... What's weighing on you today? Write a deep dive for a full AI analysis. ✨"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        className="journal-textarea-large"
                        style={{
                            width: '100%',
                            background: 'rgba(255,255,255,0.05)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '16px',
                            padding: '1.5rem',
                            paddingRight: '4rem',
                            color: 'white',
                            fontSize: '1.1rem',
                            lineHeight: '1.6',
                            resize: 'none',
                            minHeight: showHistory ? '120px' : '220px',
                            maxHeight: '400px',
                            transition: 'all 0.4s ease',
                            outline: 'none',
                            fontFamily: 'inherit'
                        }}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSubmit(e);
                            }
                        }}
                        onFocus={(e) => e.target.style.borderColor = 'var(--accent)'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                    />
                    <button
                        type="submit"
                        disabled={status === 'loading' || !content.trim()}
                        style={{
                            position: 'absolute',
                            right: '1.5rem',
                            bottom: '1.5rem',
                            background: 'var(--accent)',
                            border: 'none',
                            borderRadius: '12px',
                            width: '44px',
                            height: '44px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            cursor: 'pointer',
                            opacity: status === 'loading' || !content.trim() ? 0.5 : 1,
                            boxShadow: '0 4px 15px rgba(139, 92, 246, 0.4)',
                            transition: 'all 0.2s'
                        }}
                    >
                        {status === 'loading' ? (
                            <div className="btn-spinner" />
                        ) : (
                            <Sparkles size={20} />
                        )}
                    </button>
                </form>
            </div>
        </motion.section>
    );
}
