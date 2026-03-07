# 🔮 Vibe

Vibe is a modern, real-time community engagement platform focused on high-interaction micro-spaces called "Vibes". It’s designed to bring people together over shared interests, enabling them to chat, post, interact, and build reputation (XP) via a dynamic scoring system.

## 🚀 Features

* **Dynamic Communities (Vibes)**: Create or join topic-based micro-communities.
* **Algorithmic Feed**: A chronological and relevance-scored feed showing posts from followed users and joined vibes. 
* **Real-time Chat**: Dedicated WebSocket-powered real-time chat rooms for each Vibe.
* **Reputation System (Influence Score)**: Earn XP through meaningful engagements—creating posts, leaving comments, and receiving likes. Unlock new platform privileges (like Vibe creation) at higher levels.
* **Presence Indicators**: See exactly how many people are online in a Vibe right now.
* **Engagement Analytics**: Built-in user event tracking to seamlessly monitor engagement funnels, Day-1 retention, and platform health.
* **Modern UI/UX**: Dark-themed, responsive, and blazing-fast interface built to minimize friction and get users vibing immediately.

## 🛠 Technology Stack

### Backend
* **Framework**: Python / FastAPI
* **Database**: PostgreSQL (via Neon) + SQLite (for local testing)
* **ORM**: SQLAlchemy 2.0 (Asyncpg)
* **Migrations**: Alembic
* **Real-time**: WebSockets
* **Security**: JWT Authentication, Passlib / Bcrypt

### Frontend
* **Core**: React 18, TypeScript, Vite
* **Styling**: Tailwind CSS
* **Routing**: React Router DOM
* **Fetching**: Axios (with centralized interceptors)

---

## 💻 Local Development

Follow these steps to spin the project up locally.

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (add your database and secrets)
echo "DATABASE_URL=sqlite+aiosqlite:///./vibe.db" > .env
echo "SECRET_KEY=your_super_secret_key_here" >> .env

# Run database migrations
alembic upgrade head

# (Optional) Seed the database with starter vibes
python seed_vibes.py

# Start the FastAPI server
uvicorn app.main:app --reload --port 8008
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "VITE_API_URL=http://127.0.0.1:8008/api/v1" > .env.local

# Start the Vite development server
npm run dev
```

Your frontend should now be running on `http://localhost:5173` and connected to the backend API at `http://127.0.0.1:8008`.

---

## 🌍 Production Deployment

This project is configured out-of-the-box for cloud provider deployment.

**Backend (Render):**
The repository includes a `render.yaml` infrastructure-as-code file. Connect your GitHub repository as a new Blueprint on Render, provide your Production `DATABASE_URL` (from Neon or Supabase) and `SECRET_KEY` in the environment variables, and it will deploy instantly.

**Frontend (Vercel):**
Import the repository into Vercel, set the Framework Preset to Vite, configure the Root Directory to `frontend`, and inject your deployed backend URL into the `VITE_API_URL` environment variable.

---

## 📜 License

[MIT License](LICENSE)
