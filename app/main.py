"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import movies, preferences, feedback, auth

# Initialize FastAPI app
app = FastAPI(
    title="Moviemind API",
    description="Film recommendation platform API with cosine similarity-based recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(movies.router, prefix="/api/movies", tags=["Movies"])
app.include_router(preferences.router, prefix="/api", tags=["User Preferences"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "moviemind-api"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "moviemind-api"
    }
