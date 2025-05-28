"""
Status API Endpoints

This module provides API endpoints for checking the health and configuration
status of the TubeTrends API and its dependencies.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
from pydantic import BaseModel

from ..utils import youtube_api
from ..utils.youtube_api import YouTubeApiError # Import custom exception

router = APIRouter(tags=["status"]) # Prefix removed, will be set by main app including this router

# Response model
class StatusResponse(BaseModel):
    status: str
    message: str
    details: Dict[str, Any]

@router.get("/status", response_model=StatusResponse) # Changed path to /status
async def get_api_status():
    """
    Check the status of the API and its dependencies
    
    Returns information about:
    - API health
    - YouTube API connectivity
    - Configuration status
    """
    try:
        # Get API key from environment
        api_key = os.getenv("YOUTUBE_API_KEY")
        
        # Initialize response
        response = {
            "status": "ok",
            "message": "API is fully operational",
            "details": {
                "api_health": "ok",
                "youtube_api": "unknown",
                "configuration": {}
            }
        }
        
        # Check YouTube API key configuration
        if not api_key or api_key == "your_api_key_here":
            response["status"] = "warning"
            response["message"] = "API is running, but YouTube API key is not configured properly."
            response["details"]["youtube_api"] = "not_configured"
            response["details"]["configuration"]["youtube_api_key"] = "missing_or_placeholder"
        else:
            response["details"]["configuration"]["youtube_api_key"] = "configured"
            # Test YouTube API connectivity
            try:
                # Create YouTube API client - no longer needed as functions take api_key directly
                # youtube = youtube_api.get_youtube_client(api_key=api_key) 
                
                # Make a simple API call to test connectivity (get trending videos)
                test_result = youtube_api.get_trending_videos(api_key=api_key, max_results=1)
                
                if test_result is not None: # get_trending_videos raises error or returns list
                    response["details"]["youtube_api"] = "connected"
                # If get_trending_videos returns empty list, it implies API worked but no data.
                # The YouTubeApiError will be caught by its specific handler if API fails.

            except YouTubeApiError as yte:
                response["status"] = "error" # Changed to error as API communication failed
                response["message"] = f"YouTube API connection failed: {yte.detail}"
                response["details"]["youtube_api"] = "error_connecting"
                response["details"]["youtube_api_error"] = yte.detail
            except Exception as e: # Catch other unexpected errors during the test call
                response["status"] = "error"
                response["message"] = f"An unexpected error occurred while testing YouTube API: {str(e)}"
                response["details"]["youtube_api"] = "error_testing"
                response["details"]["youtube_api_error"] = str(e)
        
        # Check other environment variables
        redis_url = os.getenv("REDIS_URL")
        if redis_url and redis_url != "redis://localhost:6379/0":
            response["details"]["configuration"]["redis"] = "configured"
        else:
            response["details"]["configuration"]["redis"] = "default"
        
        api_secret = os.getenv("API_SECRET_KEY")
        if api_secret and api_secret != "development_secret_key":
            response["details"]["configuration"]["api_secret"] = "configured"
        else:
            response["details"]["configuration"]["api_secret"] = "development"
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
