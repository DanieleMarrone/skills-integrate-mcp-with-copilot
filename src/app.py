"""
High School Management System API

A FastAPI application that allows students to view and sign up for
extracurricular activities at Mergington High School with authentication
and role-based access control.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from database import init_db
from routers import auth, users, clubs

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities with authentication",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database tables on startup"""
    init_db()
    print("✓ Database initialized")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clubs.router)


@app.get("/")
def root():
    """Redirect to main page"""
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Mergington High School API is running"}
