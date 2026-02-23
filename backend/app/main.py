from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.endpoints import auth, checkins, users, teams, goals
from app.db.session import engine
from app.models import Base

# Create database tables (handle race conditions in multi-worker deployments)
try:
    # Check if any table exists before attempting to create all
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if not inspector.get_table_names():
        # No tables exist, create all
        Base.metadata.create_all(bind=engine)
except Exception as e:
    # Tables may already exist or other issues, continue anyway
    print(f"Database initialization note: {str(e)}")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Check-in/Check-out System API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (must be added before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Check if API is running."""
    return {"status": "ok"}


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Welcome to Check-in System API."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Handle OPTIONS requests for CORS preflight
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    """Handle OPTIONS requests for CORS preflight."""
    return JSONResponse(status_code=200, content={})


# Include routers
app.include_router(auth.router)
app.include_router(checkins.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(goals.router)


# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": str(exc),
            "error": "Internal Server Error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
