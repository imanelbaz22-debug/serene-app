import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { MessageCircle, X, Send, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './ChatBot.css';

const ChatBot = ({ isOpen, onToggle }) => {
    // const [isOpen, setIsOpen] = useState(false); // Controlled by parent now
    const [messages, setMessages] = useState([]); // Start empty as requested
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const bottomRef = useRef(null);

    // const toggleChat = () => setIsOpen(!isOpen);

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { sender: 'user', text: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        try {
            const res = await axios.post('/api/chat/message', { message: userMsg.text });

            setTimeout(() => {
                const botMsg = { sender: 'bot', text: res.data.response };
                setMessages(prev => [...prev, botMsg]);
                setIsTyping(false);
            }, 800);
        } catch (err) {
            console.error(err);
            setIsTyping(false);
            setMessages(prev => [...prev, { sender: 'bot', text: 'Sorry, I am having trouble connecting right now.' }]);
        }
    };

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping, isOpen]);

    return (
        <>
            <motion.button
                className="chat-toggle-btn"
                onClick={onToggle}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
            >
                {isOpen ? <X size={24} /> : <MessageCircle size={28} />}
            </motion.button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        className="chat-window"
                        initial={{ opacity: 0, y: 50, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 50, scale: 0.9 }}
                    >
                        <div className="chat-header">
                            <span className="chat-avatar"><Sparkles size={16} /></span>
                            <h3>Serene Assistant</h3>
                        </div>

                        <div className="chat-messages">
                            {messages.length === 0 && (
                                <div className="chat-welcome-bg">
                                    <p>welcome back bestie</p>
                                </div>
                            )}
                            {messages.map((msg, idx) => (
                                <div key={idx} className={`message-row ${msg.sender === 'user' ? 'user-row' : 'bot-row'}`}>
                                    <div className={`message-bubble ${msg.sender}`}>
                                        {msg.text}
                                    </div>
                                </div>
                            ))}
                            {isTyping && (
                                <div className="message-row bot-row">
                                    <div className="message-bubble bot typing">
                                        <span>.</span><span>.</span><span>.</span>
                                    </div>
                                </div>
                            )}
                            <div ref={bottomRef} />
                        </div>

                        <form className="chat-input-area" onSubmit={sendMessage}>
                            <input
                                type="text"
                                placeholder="Type a message..."
                                value={input}
                                onChange={e => setInput(e.target.value)}
                            />
                            <button type="submit"><Send size={18} /></button>
                        </form>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
};

export default ChatBot;
