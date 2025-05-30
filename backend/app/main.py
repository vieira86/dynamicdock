"""
Main application module for Dynamic Dock.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title="Dynamic Dock API",
    description="A molecular docking platform that enables protein-ligand docking analysis",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://dockingdynamic.netlify.app",
        "https://dynamicdock.onrender.com",
        "https://683a098f51d080dd6dd68b5b--dockingdynamic.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Dynamic Dock API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
