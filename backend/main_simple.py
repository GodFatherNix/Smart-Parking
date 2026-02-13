from fastapi import FastAPI
from app.core.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    description="Real-time parking management system",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "project": settings.project_name}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to SmartPark API",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_simple:app", host="0.0.0.0", port=8000, reload=True)
