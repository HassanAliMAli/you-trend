"""
TubeTrends API Server

FastAPI implementation for the TubeTrends application that provides YouTube trend analysis.
"""

import os
# from typing import Dict, Any # Removed unused Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import API routers
from api.trends import router as trends_router
from api.compare import router as compare_router
from api.reports import router as reports_router
from api.status import router as status_router
from utils.youtube_api import YouTubeApiError # Import the custom exception

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="TubeTrends API",
    description="API for analyzing YouTube trends and generating insights",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(YouTubeApiError)
async def youtube_api_exception_handler(request: Request, exc: YouTubeApiError) -> JSONResponse:
    """Handler for YouTubeApiError to return specific responses."""
    # Log exc.detail for server-side debugging, if needed
    return JSONResponse(
        status_code=exc.status_code, # Use status code from the exception
        content={
            "status": "error",
            "message": "Error communicating with YouTube API. Please try again later or check API key.",
            "detail": exc.detail # Optionally, include more detail if safe
        }
    )

# Add exception handler for cleaner error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the application"""
    # TODO: Log the actual exception (exc) here for server-side debugging
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected error occurred. Please try again later." # Generic message
        }
    )

# Include API routers
app.include_router(status_router, prefix="/api")
app.include_router(trends_router, prefix="/api")
app.include_router(compare_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

# Serve static files for the React frontend
# This assumes your React app is built into the `../client/build` directory
# Adjust the directory path if your build output is elsewhere
app.mount("/static", StaticFiles(directory="../client/build/static"), name="static_files")

@app.get("/{catchall:path}", include_in_schema=False)
async def serve_react_app():
    """Serves the React app's index.html for any non-API routes."""
    index_path = os.path.join(os.path.dirname(__file__), "..", "client", "build", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        status_code=404,
        content={"message": "Frontend not found. Ensure it's built correctly."}
    )

# Root endpoint now serves the React App, API docs are at /api/docs
# The @app.get("/") for API info is effectively replaced by serving index.html

if __name__ == "__main__":
    import uvicorn

    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))

    print(f"Starting TubeTrends API Server on port {port}...")
    print(f"API Documentation: http://localhost:{port}/api/docs")

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
