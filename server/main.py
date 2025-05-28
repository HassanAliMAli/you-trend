"""
TubeTrends API Server

FastAPI implementation for the TubeTrends application that provides YouTube trend analysis.
"""

import os
# from typing import Dict, Any # Removed unused Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import API routers
from api.trends import router as trends_router
from api.compare import router as compare_router
from api.reports import router as reports_router
from api.status import router as status_router
from api.users import router as users_router
from utils.youtube_api import YouTubeApiError # Import the custom exception
from utils.cache import get_redis_client, REDIS_AVAILABLE, clear_specific_cache

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
origins = [
    "http://localhost:3000",  # React local dev server
    "http://127.0.0.1:3000",
    # Add deployed frontend URLs here when available
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(YouTubeApiError)
async def youtube_api_exception_handler(request: Request, exc: YouTubeApiError) -> JSONResponse:
    """Handler for YouTubeApiError to return specific responses."""
    # Log exc.detail for server-side debugging, if needed
    return HTMLResponse(status_code=exc.status_code, content=str(exc))

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
app.include_router(users_router, prefix="/api")

# Serve static files for the React frontend
# This assumes your React app is built into the `../client/build` directory
# Adjust the directory path if your build output is elsewhere
BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client", "build"))

if os.path.exists(BUILD_DIR):
    app.mount("/static", StaticFiles(directory=os.path.join(BUILD_DIR, "static")), name="static")

    @app.get("/{full_path:path}", response_class=FileResponse, include_in_schema=False)
    async def serve_react_app(full_path: str, request: Request):
        file_path = os.path.join(BUILD_DIR, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Fallback to index.html for client-side routing
        index_path = os.path.join(BUILD_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        # If index.html also doesn't exist (which is unlikely for a built React app)
        # or if the path is for an API endpoint that wasn't matched (FastAPI handles this before static)
        # Let FastAPI handle it as a 404 for an API route or raise if it should be a file
        # For a pure SPA, any path not matched by API routers should serve index.html
        # The order of operations: API routers -> static file mount -> this catch-all.
        # If we reach here for a non-API path, it implies a file not found in build or build/static
        raise HTTPException(status_code=404, detail="File or API route not found")

else:
    print(f"Warning: Frontend build directory not found at {BUILD_DIR}. Frontend will not be served.")

@app.on_event("startup")
async def startup_event():
    if REDIS_AVAILABLE:
        print("Redis connection successful on startup.")
        # Example: Clear a specific cache on startup if needed
        # clear_specific_cache("some_prefix_*")
    else:
        print("Redis not available on startup. Cache functionality will be disabled.")

# Root endpoint now serves the React App, API docs are at /api/docs
# The @app.get("/") for API info is effectively replaced by serving index.html

if __name__ == "__main__":
    import uvicorn

    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))

    print(f"Starting TubeTrends API Server on port {port}...")
    print(f"API Documentation: http://localhost:{port}/api/docs")

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
