"""
TubeTrends API Server

FastAPI implementation for the TubeTrends application that provides YouTube trend analysis.
"""

import os
from typing import Dict, Any
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

# Add exception handler for cleaner error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the application"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc)
        }
    )

# Include API routers
app.include_router(status_router, prefix="/api")
app.include_router(trends_router, prefix="/api")
app.include_router(compare_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

# Serve static files for the React frontend
# This assumes your React app is built into the `client/build` directory
# Adjust the directory path if your build output is elsewhere
app.mount("/static_assets", StaticFiles(directory="../client/build/static"), name="static_assets")

@app.get("/{catchall:path}", include_in_schema=False)
async def serve_react_app(request: Request):
    """Serves the React app's index.html for any non-API routes."""
    return FileResponse("../client/build/index.html")

# Root endpoint now serves the React App, API docs are at /api/docs
# The @app.get("/") for API info is effectively replaced by serving index.html

if __name__ == "__main__":
    import uvicorn

    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))

    print(f"Starting TubeTrends API Server on port {port}...")
    print(f"API Documentation: http://localhost:{port}/api/docs")

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
