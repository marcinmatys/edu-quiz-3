from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import create_tables, SessionLocal
from app.db.seed import seed_database
from app.routers import debug
from .core.middleware import RateLimitingMiddleware
from .routers import quizzes, users, token, levels

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for EduQuiz application",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS settings (allow all origins for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure rate limiting
app.add_middleware(
    RateLimitingMiddleware,
    rate_limits={
        "/api/v1/quizzes": {"rate": 5, "per": 60, "burst": 5},  # 5 requests per minute, burst of 5
        "/api/v1/auth/token": {"rate": 3, "per": 60, "burst": 3}  # 3 login attempts per minute, burst of 3
    }
)

# Initialize database tables and seed data on startup
@app.on_event("startup")
async def startup_db_client():
    await create_tables()
    print("Database tables created.")
    
    # Seed the database with initial data (async session, since seed_database is now async)
    async with SessionLocal() as db:
        await seed_database(db)

@app.get("/ping")
def ping():
    return {"message": "pong"}

# Include routers
app.include_router(debug.router)
app.include_router(quizzes.router)
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(token.router)
app.include_router(levels.router)

# Import and include routers here for future scalability
# from .routers import example_router
# app.include_router(example_router)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
