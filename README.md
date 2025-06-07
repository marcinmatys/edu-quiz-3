# EduQuiz Project Structure

This project is split into two main parts:
- **frontend/**: React 19 + Vite + Tailwind + Shadcn/ui (student/admin UI)
- **backend/**: Python FastAPI + SQLite (API server)

## Directory Layout

```
/backend/           # FastAPI backend
/frontend/          # React frontend
/README.md          # Project-level documentation
```

## Setup Instructions

### Frontend

1. Open a terminal in the `frontend/` directory:
   ```sh
   cd frontend
   npm install
   npm run dev
   ```
2. The frontend will start on its default Vite port (usually 5173).

### Backend

1. Open a terminal in the `backend/` directory:
   ```sh
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
2. The backend will start on http://127.0.0.1:8000
3. Test endpoint: http://127.0.0.1:8000/ping

## Development Notes
- Frontend and backend run separately.
- CORS is enabled for local development.
- Backend is organized for future scalability (routers, models, schemas, db, core).
- Use SQLite for local development.

---

For more details, see `doc/backend-base-config.md`.
