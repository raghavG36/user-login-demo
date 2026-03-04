"""
FastAPI application entry point.
Database tables are created on startup; routers mounted at /auth and /calculator.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth.router import router as auth_router
from app.api.calculator.router import router as calculator_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup; cleanup on shutdown."""
    await init_db()
    yield
    # Optional: close engine / cleanup here if needed


app = FastAPI(
    title="FastAPI User Login & Calculator",
    description="Production-ready API with JWT auth and protected calculator.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for React frontend (dev: localhost:3000; adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(calculator_router)


@app.get("/health")
async def health():
    """Health check for load balancers and container orchestration."""
    return {"status": "ok"}
