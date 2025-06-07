# Backend Base Configuration

## Requirements Summary

- Add a Python FastAPI backend to the project.
- Use a separate `backend/` directory at the project root for backend code.
- Move all frontend code and config files into a `frontend/` directory.
- Backend and frontend should run separately (not served together).
- Use SQLite for local development database.
- Only a single test endpoint is needed initially (no full API design yet).
- No authentication or Docker setup required at this stage.
- Organize backend code for future scalability (routers, models, schemas, db, core).
- Enable CORS in FastAPI for frontend-backend communication.
- Use `.gitignore` for both Python and Node.js artifacts.

---

## Detailed Plan

### 1. Directory Structure

```
/backend/           # FastAPI backend (new)
/frontend/          # React frontend (move all frontend code here)
/README.md          # Project-level documentation
```

### 2. Frontend Migration
- Create a new `frontend/` directory at the project root.
- Move all frontend source code (`src/`) and config files (`package.json`, `vite.config.js`, `tailwind.config.js`, etc.) into `frontend/`.
- Update any scripts or documentation to use the new paths.

### 3. Backend Setup
- Create a new `backend/` directory at the project root.
- Inside `backend/`:
  - Set up a Python virtual environment.
  - Add a `requirements.txt` with:
    - `fastapi`
    - `uvicorn`
    - `sqlalchemy`
    - `pydantic`
  - Create base FastAPI app structure:
    - `backend/app/main.py` (entry point)
    - Add a single test endpoint (e.g., `/ping`)
    - Organize folders for future code:
      - `routers/` (API endpoints)
      - `models/` (SQLAlchemy models)
      - `schemas/` (Pydantic schemas)
      - `db/` (database setup)
      - `core/` (settings, utils)
      - `config.py` (configuration)
  - Add a `.gitignore` for Python/venv files.

### 4. Database
- Use SQLite for local development.
- Set up SQLAlchemy ORM in `backend/app/db/`.
- (Optional) Organize code so Alembic migrations can be added later if needed.

### 5. CORS & Frontend Integration
- Enable CORS in FastAPI to allow requests from the frontend.

### 6. Dev Workflow
- Add scripts for running the backend (e.g., `uvicorn app.main:app --reload`).
- Document backend and frontend setup in the main `README.md`.

### 7. Version Control
- Ensure `.gitignore` covers both Python and Node.js artifacts in their respective directories.

---

**Notes:**
- Alembic is not required now, but code should be organized for easy future integration.
- Pydantic schemas will be used for data validation and serialization in FastAPI endpoints.
- Only a test endpoint (e.g., `/ping`) is needed for the initial backend setup. 