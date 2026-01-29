import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart3, Trophy, Target, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

const API_URL = '/api';

export default function WeeklyReport() {
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchReport = async () => {
            try {
                const res = await axios.get(`${API_URL}/analytics/reports/weekly`);
                setReport(res.data);
            } catch (err) {
                console.error("Failed to fetch weekly report", err);
            } finally {
                setLoading(false);
            }
        };
        fetchReport();
    }, []);

    if (loading) return null;
    if (!report) return null;

    return (
        <motion.section
            className="card report-card"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
        >
            <div className="report-header">
                <h2><BarChart3 size={24} className="icon-title" /> Weekly Summary</h2>
                <p className="ai-badge"><Sparkles size={14} /> AI Generated</p>
            </div>

            <div className="report-content" style={{ marginTop: '1rem' }}>
                <p className="report-summary" style={{
                    fontSize: '1.1rem',
                    lineHeight: '1.6',
                    fontStyle: 'italic',
                    color: 'rgba(255, 255, 255, 0.9)',
                    marginBottom: '2rem',
                    padding: '1rem',
                    background: 'rgba(255, 255, 255, 0.05)',
                    borderLeft: '3px solid var(--accent)',
                    borderRadius: '0 10px 10px 0'
                }}>"{report.summary}"</p>

                <div className="report-highlights" style={{
                    display: 'grid',
                    gridTemplateColumns: window.innerWidth > 600 ? '1fr 1fr' : '1fr',
                    gap: '1rem'
                }}>
                    <div className="highlight-item win" style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '1rem',
                        padding: '1rem',
                        borderRadius: '12px',
                        background: 'rgba(255, 255, 255, 0.03)',
                        border: '1px solid rgba(255, 255, 255, 0.05)'
                    }}>
                        <div className="highlight-icon" style={{
                            padding: '0.8rem',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: 'rgba(250, 204, 21, 0.1)',
                            color: '#facc15'
                        }}><Trophy size={20} /></div>
                        <div className="highlight-text" style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.5rem'
                        }}>
                            <strong style={{
                                fontSize: '0.85rem',
                                textTransform: 'uppercase',
                                color: 'var(--text-secondary)',
                                letterSpacing: '0.5px'
                            }}>Biggest Win</strong>
                            <span style={{
                                fontSize: '1rem',
                                fontWeight: '600',
                                color: 'white',
                                lineHeight: '1.4'
                            }}>{report.win}</span>
                        </div>
                    </div>

                    <div className="highlight-item focus" style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '1rem',
                        padding: '1rem',
                        borderRadius: '12px',
                        background: 'rgba(255, 255, 255, 0.03)',
                        border: '1px solid rgba(255, 255, 255, 0.05)'
                    }}>
                        <div className="highlight-icon" style={{
                            padding: '0.8rem',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: 'rgba(239, 68, 68, 0.1)',
                            color: '#ef4444'
                        }}><Target size={20} /></div>
                        <div className="highlight-text" style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.5rem'
                        }}>
                            <strong style={{
                                fontSize: '0.85rem',
                                textTransform: 'uppercase',
                                color: 'var(--text-secondary)',
                                letterSpacing: '0.5px'
                            }}>Focus Area</strong>
                            <span style={{
                                fontSize: '1rem',
                                fontWeight: '600',
                                color: 'white',
                                lineHeight: '1.4'
                            }}>{report.focus}</span>
                        </div>
                    </div>
                </div>
            </div>
        </motion.section>
    );
}
