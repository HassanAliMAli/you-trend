"""
Trends API Endpoints

This module provides API endpoints for analyzing YouTube trends,
including video search, trending videos, and trend analysis.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# Assuming utils are in PYTHONPATH or adjusted relative import if needed
# For local structure: from ..utils import youtube_api, data_processor
from ..utils import youtube_api
from ..utils import data_processor
from ..utils.youtube_api import YouTubeApiError

# For user authentication (optional)
from ..utils import database, auth
from ..models.user import User as UserModel

router = APIRouter(prefix="/trends", tags=["trends"])

# --- Pydantic Models for POST request bodies ---
class TrendsRequestBody(BaseModel):
    api_key_query: Optional[str] = Field(default=None, description="Optional: YouTube Data API v3 key. Overrides user's saved key or system key.", alias="api_key")
    query: Optional[str] = Field(default=None, description="Search term for videos. If empty, fetches general trending videos.")
    category: Optional[str] = Field(default=None, description="Video category ID (used if query is empty for general trending)")
    country: str = Field(default="PK", description="Country code (e.g., 'PK', 'US')")
    duration: Optional[str] = Field(default=None, description="Duration filter ('Short (< 4 minutes)', 'Medium (4-20 minutes)', 'Long (> 20 minutes)')")
    max_results: int = Field(default=10, description="Maximum number of results (default: 10, max: 50)", ge=1, le=50)
    order: str = Field(default="viewCount", description="Sort order for search ('viewCount', 'relevance', 'rating', 'date')")
    published_after: Optional[str] = Field(default=None, description="Filter videos published after this date (YYYY-MM-DDTHH:MM:SSZ)")
    published_before: Optional[str] = Field(default=None, description="Filter videos published before this date (YYYY-MM-DDTHH:MM:SSZ)")
    language: Optional[str] = Field(default=None, description="Filter videos relevant to a specific language (ISO 639-1 code)")

    class Config:
        allow_population_by_field_name = True

class ChannelsRequestBody(BaseModel):
    api_key_query: Optional[str] = Field(default=None, description="Optional: YouTube Data API v3 key. Overrides user's or system key.", alias="api_key")
    query: Optional[str] = Field(default=None, description="Search term for channels. If empty, this might not yield useful general results without further logic.")
    country: str = Field(default="PK", description="Country code (e.g., 'PK', 'US') for search region bias")
    max_results: int = Field(default=10, description="Maximum number of channels to return (default: 10, max: 50)", ge=1, le=50)

    class Config:
        allow_population_by_field_name = True
# --- End Pydantic Models ---

@router.post("", response_model=None)
async def get_trends_via_post(
    request_data: TrendsRequestBody = Body(...),
    db: Session = Depends(database.get_db),
    current_user: Optional[UserModel] = Depends(auth.get_current_user_optional)
):
    """
    Get trending videos and analysis based on search parameters via POST.
    If query is provided, performs a search. Otherwise, fetches general trending videos.
    Prioritizes API key: query parameter > authenticated user's key > system .env key.
    """
    final_api_key_to_use = request_data.api_key_query
    if not final_api_key_to_use and current_user and current_user.youtube_api_key:
        final_api_key_to_use = current_user.youtube_api_key

    try:
        videos: List[Dict[str, Any]] = []
        if request_data.query:
            videos = youtube_api.search_videos(
                query=request_data.query,
                max_results=request_data.max_results,
                country=request_data.country,
                video_duration=request_data.duration,
                order=request_data.order,
                published_after=request_data.published_after,
                published_before=request_data.published_before,
                relevance_language=request_data.language,
                api_key=final_api_key_to_use
            )
        elif request_data.category:
            videos = youtube_api.get_trending_videos(
                region_code=request_data.country,
                category_id=request_data.category,
                max_results=request_data.max_results,
                api_key=final_api_key_to_use
            )
        else:
            videos = youtube_api.get_trending_videos(
                region_code=request_data.country,
                max_results=request_data.max_results,
                api_key=final_api_key_to_use
            )
        
        if not videos:
            return {
                "status": "success",
                "message": "No videos found matching your criteria.",
                "data": {
                    "total_videos_analyzed": 0,
                    "average_views": 0,
                    "average_engagement_rate": 0,
                    "top_videos": [],
                    "trending_topics": [],
                    "video_ideas": []
                }
            }

        video_analysis_results = data_processor.analyze_video_trends(videos, top_n_videos=request_data.max_results, top_n_topics=10)
        
        video_ideas = data_processor.generate_video_ideas(
            topics=video_analysis_results.get("trending_topics", []),
            videos=video_analysis_results.get("top_videos", []),
            top_n_ideas=10
        )
        
        response_data = {
            "total_videos_analyzed": video_analysis_results.get("total_videos_analyzed", 0),
            "average_views": video_analysis_results.get("average_views", 0),
            "average_engagement_rate": video_analysis_results.get("average_engagement_rate", 0),
            "top_videos": video_analysis_results.get("top_videos", []),
            "trending_topics": video_analysis_results.get("trending_topics", []),
            "video_ideas": video_ideas
        }
        
        return {
            "status": "success",
            "message": f"Successfully analyzed {len(videos)} videos.",
            "data": response_data
        }
        
    except YouTubeApiError as yte:
        raise HTTPException(status_code=yte.status_code, detail=yte.detail)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/channels", response_model=None)
async def get_trending_channels_via_post(
    request_data: ChannelsRequestBody = Body(...),
    db: Session = Depends(database.get_db),
    current_user: Optional[UserModel] = Depends(auth.get_current_user_optional)
):
    """
    Get trending channels based on search parameters via POST.
    Prioritizes API key: query parameter > authenticated user's key > system .env key.
    """
    if not request_data.query:
         raise HTTPException(status_code=400, detail="A search query is required to find channels.")

    final_api_key_to_use = request_data.api_key_query
    if not final_api_key_to_use and current_user and current_user.youtube_api_key:
        final_api_key_to_use = current_user.youtube_api_key

    try:
        channels_details = youtube_api.search_channels(
            query=request_data.query,
            max_results=request_data.max_results,
            region_code=request_data.country,
            api_key=final_api_key_to_use
        )
        
        if not channels_details:
            return {
                "status": "success",
                "message": "No channels found matching your criteria.",
                "data": {
                    "total_channels_analyzed": 0,
                    "average_subscribers": 0,
                    "top_channels": []
                }
            }

        videos_by_channel_map: Dict[str, List[Dict[str, Any]]] = {}
        if channels_details:
            for channel_data in channels_details[:5]:
                channel_id = channel_data.get('id')
                if channel_id:
                    channel_videos = youtube_api.get_channel_videos(
                        channel_id=channel_id,
                        max_results=10,
                        order='viewCount',
                        api_key=final_api_key_to_use
                    )
                    videos_by_channel_map[channel_id] = channel_videos
        
        channel_analysis_results = data_processor.analyze_channel_trends(
            channels_details=channels_details,
            videos_by_channel=videos_by_channel_map,
            top_n_channels=request_data.max_results
        )
        
        return {
            "status": "success",
            "message": f"Successfully analyzed channels.",
            "data": channel_analysis_results
        }
        
    except YouTubeApiError as yte:
        raise HTTPException(status_code=yte.status_code, detail=yte.detail)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/categories", response_model=None)
async def get_video_categories_endpoint(
    api_key_query: Optional[str] = Query(None, description="Optional: YouTube Data API v3 key. Overrides user's or system key.", alias="api_key"),
    country: str = Query("PK", description="Country code (e.g., 'PK', 'US')"),
    db: Session = Depends(database.get_db),
    current_user: Optional[UserModel] = Depends(auth.get_current_user_optional)
):
    """
    Get available video categories for a region.
    Prioritizes API key: query parameter > authenticated user's key > system .env key.
    """
    final_api_key_to_use = api_key_query
    if not final_api_key_to_use and current_user and current_user.youtube_api_key:
        final_api_key_to_use = current_user.youtube_api_key

    try:
        categories = youtube_api.get_video_categories(region_code=country, api_key=final_api_key_to_use)
        return {
            "status": "success",
            "message": f"Found {len(categories)} video categories for region {country}",
            "data": {"categories": categories}
        }
    except YouTubeApiError as yte:
        raise HTTPException(status_code=yte.status_code, detail=yte.detail)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
