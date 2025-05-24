"""
Status API Endpoints

This module provides API endpoints for checking the health and configuration
status of the TubeTrends API and its dependencies.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
from pydantic import BaseModel

from utils import youtube_api

router = APIRouter(prefix="/api/status", tags=["status"])

# Response model
class StatusResponse(BaseModel):
    status: str
    message: str
    details: Dict[str, Any]

@router.get("", response_model=StatusResponse)
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
            response["message"] = "API is running, but YouTube API key is not configured"
            response["details"]["youtube_api"] = "not_configured"
            response["details"]["configuration"]["youtube_api_key"] = "missing"
        else:
            # Test YouTube API connectivity
            try:
                # Create YouTube API client
                youtube = youtube_api.get_youtube_client()
                
                # Make a simple API call to test connectivity (get trending videos)
                test_result = youtube_api.get_trending_videos(max_results=1)
                
                if test_result:
                    response["details"]["youtube_api"] = "connected"
                    response["details"]["configuration"]["youtube_api_key"] = "configured"
                else:
                    response["status"] = "warning"
                    response["message"] = "API is running, but YouTube API returned no data"
                    response["details"]["youtube_api"] = "error"
                    response["details"]["configuration"]["youtube_api_key"] = "configured_but_error"
            except Exception as e:
                response["status"] = "warning"
                response["message"] = f"API is running, but YouTube API connection failed: {str(e)}"
                response["details"]["youtube_api"] = "error"
                response["details"]["configuration"]["youtube_api_key"] = "configured_but_error"
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
