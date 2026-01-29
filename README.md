# Serene - Your AI Mental Wellness Companion 🌿✨


Serene is a modern mental wellness application designed to help you track your mood, gain deeper insights into your well-being, and find balance through AI-powered journaling.

Built with a focus on privacy, aesthetics, and meaningful interactions, Serene acts as your "AI Bestie" — safe, supportive, and always there to listen.

## ✨ Key Features

- **Daily Check-ins**: Track your Mood, Energy, and Sleep with intuitive sliders.
- **Deep Dive Journal**: Write freely in a distraction-free space.
- **AI Analysis**: Get instant, empathetic feedback and "Smart Insights" on your journal entries.
- **Mood Forecasting**: Predict your future emotional trends based on historical data.
- **Serene Assistant**: A context-aware AI chatbot that remembers your past conversations (powered by Google Gemini).
- **Weekly Reports**: Visual summaries of your emotional week.
- **Secure & Private**: Authentication via Clerk, ensuring your data is yours alone.

## 🛠️ Tech Stack

### Frontend
- **React 19** (Vite)
- **Framer Motion** (Animations)
- **Recharts** (Data Visualization)
- **Clerk** (Authentication)
- **Lucide React** (Icons)
- **Vanilla CSS** (Custom Design System)

### Backend
- **Python 3.10+** (FastAPI)
- **Google Gemini 1.5** (AI Models)
- **PostgreSQL** (Neon.tech - Serverless DB)
- **SQLAlchemy** (ORM)

### Deployment
- **Google Cloud Run** (Serverless Container)
- **Docker** (Containerization)

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- A [Clerk](https://clerk.com) account
- A [Google Gemini API Key](https://ai.google.dev/)
- A [Neon.tech](https://neon.tech) PostgreSQL database

### Local Development

1.  **Clone the repository**
    ```bash
    git clone https://github.com/imanelbaz22-debug/serene-app.git
    cd serene-app
    ```

2.  **Setup Backend**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in `backend/` and add:
    ```env
    DATABASE_URL=postgresql://user:pass@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require
    GEMINI_API_KEY=your_gemini_key
    CLERK_SECRET_KEY=your_clerk_secret_key
    VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
    ```

4.  **Run Backend**
    ```bash
    uvicorn app.main:app --reload
    ```

5.  **Setup Frontend** (Open a new terminal)
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

    Visit `http://localhost:5173` to see the app!

## 🐳 Deployment (Google Cloud Run)

Serene is optimized for Google Cloud Run.

1.  **Build the Frontend**
    ```bash
    cd frontend
    npm run build
    ```

2.  **Copy Assets to Backend**
    ```bash
    # From project root
    cp -r frontend/dist backend/frontend_dist
    ```

3.  **Deploy**
    ```bash
    cd backend
    gcloud run deploy serene-app --source .
    ```

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a Pull Request.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
