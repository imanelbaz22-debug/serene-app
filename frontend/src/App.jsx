import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Sparkles, Activity, Moon, Send, TrendingUp, AlertCircle, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { SignedIn, SignedOut, SignIn, SignUp, UserButton, useAuth } from '@clerk/clerk-react';
import ChatBot from './components/ChatBot';
import Journal from './components/Journal';
import WeeklyReport from './components/WeeklyReport';
import './App.css';

const API_URL = '/api';

function App() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [showSignUp, setShowSignUp] = useState(false);

  // 🚀 DEVELOPMENT BYPASS STATE
  const [isMockLoggedIn, setIsMockLoggedIn] = useState(localStorage.getItem('serene_mock_auth') === 'true');

  const [formData, setFormData] = useState({
    mood: 5,
    energy: 5,
    sleep_hours: 7.0,
    text: '',
  });

  const [forecast, setForecast] = useState(null);
  const [insights, setInsights] = useState(null);
  const [streak, setStreak] = useState(0);
  const [status, setStatus] = useState('idle');
  const [message, setMessage] = useState('');
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Setup axios interceptor for auth
  useEffect(() => {
    const interceptor = axios.interceptors.request.use(
      async (config) => {
        // Use Mock Token if in bypass mode
        if (localStorage.getItem('serene_mock_auth') === 'true') {
          config.headers['Authorization'] = `Bearer mock_bestie_token`;
          return config;
        }

        const token = await getToken();
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
      }
    );
    return () => axios.interceptors.request.eject(interceptor);
  }, [getToken]);

  const fetchData = async () => {
    if (!isSignedIn && !isMockLoggedIn) return;

    // Fetch Forecast (might fail if not enough data)
    try {
      const forecastRes = await axios.get(`${API_URL}/analytics/mood-forecast`);
      setForecast(forecastRes.data);
    } catch (err) {
      console.log("Forecast unavailable (likely insufficient data)");
      setForecast(null);
    }

    // Fetch Insights
    try {
      const insightsRes = await axios.get(`${API_URL}/analytics/insights/latest`);
      setInsights(insightsRes.data);
    } catch (err) {
      console.error("Insights fetch failed", err);
    }

    // Fetch Streak (Critical for UI)
    try {
      const streakRes = await axios.get(`${API_URL}/analytics/streak`);
      setStreak(streakRes.data.streak);
    } catch (err) {
      console.error("Streak fetch failed", err);
    }
  };

  useEffect(() => {
    if (isLoaded && (isSignedIn || isMockLoggedIn)) {
      fetchData();
    }
  }, [isLoaded, isSignedIn, isMockLoggedIn]);

  const handleMockLogin = () => {
    localStorage.setItem('serene_mock_auth', 'true');
    setIsMockLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('serene_mock_auth');
    setIsMockLoggedIn(false);
    // Clerk handles its own logout via UserButton or Clerk.signOut()
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('loading');
    try {
      await axios.post(`${API_URL}/checkins/`, formData);
      setStatus('success');
      setMessage('Check-in saved successfully!');
      setFormData({ mood: 5, energy: 5, sleep_hours: 7.0, text: '' });
      fetchData();
      setTimeout(() => setStatus('idle'), 2000);
    } catch (err) {
      console.error(err);
      setStatus('error');
      setMessage('Failed to save check-in.');
    }
  };

  if (!isLoaded) return <div className="loading-screen">Serene is waking up... 😴✨</div>;

  // Final rendering logic
  const effectivelyLoggedIn = isSignedIn || isMockLoggedIn;

  // Clerk Appearance for Dark Theme
  const clerkAppearance = {
    variables: {
      colorPrimary: '#8b5cf6', // Violet-500
      colorText: 'white',
      colorBackground: '#1e1b4b', // Dark purple/blue bg
      colorInputBackground: 'rgba(255, 255, 255, 0.05)',
      colorInputText: 'white',
      fontFamily: 'inherit',
      borderRadius: '12px',
    },
    elements: {
      card: {
        backdropFilter: 'blur(12px)',
        backgroundColor: 'rgba(30, 27, 75, 0.8)', // Darker semi-transparent
        border: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.5)',
      },
      headerTitle: { color: 'white' },
      headerSubtitle: { color: '#94a3b8' },
      socialButtonsBlockButton: {
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        color: 'white',
      },
      socialButtonsBlockButtonText: { color: 'white' },
      formButtonPrimary: {
        background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
        boxShadow: '0 4px 15px rgba(139, 92, 246, 0.4)',
        border: 'none',
      },
      footerActionLink: { color: '#8b5cf6' },
      formFieldLabel: { color: '#94a3b8' },
      formFieldInput: {
        borderColor: 'rgba(255,255,255,0.1)',
        color: 'white'
      },
      identityPreviewText: { color: 'white' },
      identityPreviewEditButtonIcon: { color: '#8b5cf6' }
    }
  };

  return (
    <>
      {!effectivelyLoggedIn ? (
        <div className="auth-container">
          <div className="auth-split">
            <motion.div
              className="auth-hero"
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <Sparkles className="auth-logo" size={60} />
              <h1>Your AI Bestie Awaits. 💖</h1>
              <p>Join thousands finding balance with Serene.</p>
            </motion.div>

            <motion.div
              className="auth-form-wrapper"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <div className="clerk-bypass-toggle">
                <button className="btn-secondary-link" onClick={() => setShowSignUp(!showSignUp)}>
                  {showSignUp ? "Back to Login" : "Need an account? Sign up"}
                </button>
              </div>

              <AnimatePresence mode="wait">
                {showSignUp ? (
                  <motion.div key="signup" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                    <SignUp routing="hash" appearance={clerkAppearance} />
                  </motion.div>
                ) : (
                  <motion.div key="signin" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                    <SignIn routing="hash" appearance={clerkAppearance} />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>
        </div>
      ) : (
        <div className="container">
          <header className="header">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="header-content"
            >
              <div className="title-row">
                <div className="title-left">
                  <h1><Sparkles className="icon-title" /> Serene</h1>
                  {streak > 0 && (
                    <motion.div
                      className="streak-badge"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      whileHover={{ scale: 1.1 }}
                    >
                      {streak} 🔥
                    </motion.div>
                  )}
                </div>
                <div className="user-profile">
                  {isMockLoggedIn ? (
                    <button className="btn-logout" onClick={handleLogout}>
                      <LogOut size={18} /> Exit Bypass
                    </button>
                  ) : (
                    <UserButton afterSignOutUrl="/" appearance={clerkAppearance} />
                  )}
                </div>
              </div>
              <p>Track your well-being, predict your flow.</p>
            </motion.div>
          </header>

          <main className="grid">
            {/* Daily Check-in */}
            <motion.section className="card" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
              <h2>Daily Check-in</h2>
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label><Activity size={18} /> Mood ({formData.mood})</label>
                  <input type="range" min="1" max="10" value={formData.mood} onChange={e => setFormData({ ...formData, mood: parseInt(e.target.value) })} className="slider mood-slider" />
                </div>
                <div className="form-group">
                  <label><TrendingUp size={18} /> Energy ({formData.energy})</label>
                  <input type="range" min="1" max="10" value={formData.energy} onChange={e => setFormData({ ...formData, energy: parseInt(e.target.value) })} className="slider energy-slider" />
                </div>
                <div className="form-group">
                  <label><Moon size={18} /> Sleep ({formData.sleep_hours}h)</label>
                  <input type="number" step="0.5" value={formData.sleep_hours} onChange={e => setFormData({ ...formData, sleep_hours: parseFloat(e.target.value) })} className="number-input" />
                </div>
                <div className="form-group">
                  <label>Notes</label>
                  <textarea placeholder="How are you feeling properly?" value={formData.text} onChange={e => setFormData({ ...formData, text: e.target.value })} rows={3} />
                </div>
                <button type="submit" className="btn-primary" disabled={status === 'loading'}>
                  {status === 'loading' ? 'Saving...' : <><Send size={18} /> Check In</>}
                </button>
                {status === 'success' && <p className="status-success">{message}</p>}
                {status === 'error' && <p className="status-error"><AlertCircle size={16} /> {message}</p>}
              </form>
            </motion.section>

            <section className="right-column">
              {insights && (
                <motion.div className="card insights-card" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}>
                  <h2><Sparkles size={20} className="icon-title" /> Smart Insights</h2>
                  <div className="insights-section" style={{ color: 'white' }}>
                    <h3>Likely Causes</h3>
                    <ul>{insights.reasons.length > 0 ? insights.reasons.map((r, i) => <li key={i}>{r}</li>) : <li>Gathering context...</li>}</ul>
                  </div>
                  <div className="insights-section" style={{ color: 'white' }}>
                    <h3>Recommended Tips</h3>
                    <ul>{insights.tips.length > 0 ? insights.tips.map((t, i) => <li key={i}>{t}</li>) : <li>Checking in more helps!</li>}</ul>
                  </div>
                </motion.div>
              )}

              <motion.section className="card forecast-card" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
                <h2>Mood Forecast</h2>
                {forecast ? (
                  <div className="forecast-content">
                    <div className="stat-row">
                      <div className="stat"><span className="label">Next Prediction</span><span className="value">{forecast.next_day_prediction}/10</span></div>
                      <div className="stat"><span className="label">Trend Slope</span><span className={`value ${forecast.trend_slope >= 0 ? 'pos' : 'neg'}`}>{forecast.trend_slope > 0 ? '+' : ''}{forecast.trend_slope}</span></div>
                    </div>
                    <div className="chart-wrapper">
                      <ResponsiveContainer width="100%" height={100}>
                        <LineChart data={[{ val: 5 }, { val: forecast.next_day_prediction - forecast.trend_slope }, { val: forecast.next_day_prediction }]}><Line type="monotone" dataKey="val" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} /><Tooltip /></LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                ) : <p className="loading-text">Gathering insights...</p>}
              </motion.section>
            </section>

            <WeeklyReport />
            <Journal onOpenChat={() => setIsChatOpen(true)} />
          </main>
          <ChatBot isOpen={isChatOpen} onToggle={() => setIsChatOpen(!isChatOpen)} />
        </div>
      )}
    </>
  );
}

export default App;
