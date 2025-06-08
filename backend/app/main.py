from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import create_tables, SessionLocal
from app.db.seed import seed_database
from app.routers import debug

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

# CORS settings (allow all origins for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables and seed data on startup
@app.on_event("startup")
def startup_db_client():
    create_tables()
    print("Database tables created.")
    
    # Seed the database with initial data
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

@app.get("/ping")
def ping():
    return {"message": "pong"}

# Include routers
app.include_router(debug.router)

# Import and include routers here for future scalability
# from .routers import example_router
# app.include_router(example_router)
