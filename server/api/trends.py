"""
Trends API Endpoints

This module provides API endpoints for analyzing YouTube trends,
including video search, trending videos, and trend analysis.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional, Any
# from pydantic import BaseModel # BaseModel for request body not used here, using Query params

# Assuming utils are in PYTHONPATH or adjusted relative import if needed
# For local structure: from ..utils import youtube_api, data_processor
import utils.youtube_api as youtube_api
import utils.data_processor as data_processor
from utils.youtube_api import YouTubeApiError

router = APIRouter(prefix="/trends", tags=["trends"])

# Updated Response model to reflect new structure (example)
# This can be more formally defined with Pydantic if desired for strict validation
# class VideoTrendData(BaseModel):
#     total_videos_analyzed: int
#     average_views: float
#     average_engagement_rate: float
#     top_videos: List[Dict]
#     trending_topics: List[Dict]
#     video_ideas: List[Dict]

# class TrendsResponse(BaseModel):
#     status: str
#     message: str
#     data: VideoTrendData

@router.get("", response_model=None) # Using None or Dict for more flexible response initially
async def get_trends(
    api_key: str = Query(..., description="YouTube Data API v3 key (required)"),
    query: Optional[str] = Query(None, description="Search term for videos. If empty, fetches general trending videos."),
    category: Optional[str] = Query(None, description="Video category ID (used if query is empty for general trending)"),
    country: str = Query("PK", description="Country code (e.g., 'PK', 'US')"),
    duration: Optional[str] = Query(None, description="Duration filter ('Short (< 4 minutes)', 'Medium (4-20 minutes)', 'Long (> 20 minutes)')"),
    max_results: int = Query(10, description="Maximum number of results (default: 10, max: 50)", ge=1, le=50),
    order: str = Query("viewCount", description="Sort order for search ('viewCount', 'relevance', 'rating', 'date')"),
    published_after: Optional[str] = Query(None, description="Filter videos published after this date (YYYY-MM-DDTHH:MM:SSZ)"),
    published_before: Optional[str] = Query(None, description="Filter videos published before this date (YYYY-MM-DDTHH:MM:SSZ)"),
    language: Optional[str] = Query(None, description="Filter videos relevant to a specific language (ISO 639-1 code)")
):
    """
    Get trending videos and analysis based on search parameters.
    If query is provided, performs a search. Otherwise, fetches general trending videos.
    """
    # No explicit api_key check here, as youtube_api functions will use env var or raise error
    # However, FastAPI Query(..., makes it required if not supplied via env by those funcs
    
    try:
        videos: List[Dict[str, Any]] = []
        if query:
            videos = youtube_api.search_videos(
                query=query,
                max_results=max_results,
                country=country,
                video_duration=duration,
                order=order,
                published_after=published_after,
                published_before=published_before,
                relevance_language=language,
                api_key=api_key # Explicitly pass for clarity, though utils handle fallback
            )
        elif category: # Only fetch general trending if no query but category is specified
            videos = youtube_api.get_trending_videos(
                region_code=country,
                category_id=category,
                max_results=max_results,
                api_key=api_key
            )
        else: # Default to general trending for the country if no query and no category
            videos = youtube_api.get_trending_videos(
                region_code=country,
                max_results=max_results,
                api_key=api_key
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

        # Perform trend analysis using the new structure from data_processor
        video_analysis_results = data_processor.analyze_video_trends(videos, top_n_videos=max_results, top_n_topics=10)
        
        # Generate video ideas using the topics from analysis and the fetched videos
        # Note: analyze_video_trends now returns top_videos and trending_topics directly
        video_ideas = data_processor.generate_video_ideas(
            topics=video_analysis_results.get("trending_topics", []),
            videos=video_analysis_results.get("top_videos", []), # Use top_videos from analysis for idea generation context
            top_n_ideas=10
        )
        
        # Construct response data
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
    except ValueError as ve: # Catch potential ValueError from date parsing etc.
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Log the exception for debugging
        # import traceback; traceback.print_exc();
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/channels", response_model=None) # Using None or Dict for more flexible response initially
async def get_trending_channels(
    api_key: str = Query(..., description="YouTube Data API v3 key (required)"),
    query: Optional[str] = Query(None, description="Search term for channels. If empty, this might not yield useful general results without further logic."),
    country: str = Query("PK", description="Country code (e.g., 'PK', 'US') for search region bias"),
    max_results: int = Query(10, description="Maximum number of channels to return (default: 10, max: 50)", ge=1, le=50)
):
    """
    Get trending channels based on search parameters.
    Note: YouTube API doesn't have a direct 'trending channels' like 'trending videos'. 
    This searches channels by query and then analyzes them.
    If query is empty, behavior might be undefined or fetch very broad results.
    """
    if not query:
         raise HTTPException(status_code=400, detail="A search query is required to find channels.")

    try:
        channels_details = youtube_api.search_channels(
            query=query,
            max_results=max_results,
            region_code=country,
            api_key=api_key
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

        # Fetch some videos for each channel to help with scoring (avg views, frequency)
        # This can be quota-intensive if max_results is high.
        videos_by_channel_map: Dict[str, List[Dict[str, Any]]] = {}
        if channels_details: # only proceed if channels were found
            for channel_data in channels_details[:5]: # Analyze top 5 results to limit quota usage
                channel_id = channel_data.get('id')
                if channel_id:
                    # Fetch a small number of recent or top videos for channel scoring
                    channel_videos = youtube_api.get_channel_videos(
                        channel_id=channel_id,
                        max_results=10, # Number of videos to fetch per channel for scoring
                        order='viewCount',
                        api_key=api_key
                    )
                    videos_by_channel_map[channel_id] = channel_videos
        
        # Perform channel trend analysis using the new structure from data_processor
        channel_analysis_results = data_processor.analyze_channel_trends(
            channels_details=channels_details, 
            videos_by_channel=videos_by_channel_map, 
            top_n_channels=max_results
        )
        
        return {
            "status": "success",
            "message": f"Successfully analyzed channels.",
            "data": channel_analysis_results # Return the whole analysis dict
        }
        
    except YouTubeApiError as yte:
        raise HTTPException(status_code=yte.status_code, detail=yte.detail)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/categories", response_model=None) # Using None or Dict for more flexible response initially
async def get_video_categories_endpoint(
    api_key: str = Query(..., description="YouTube Data API v3 key (required)"),
    country: str = Query("PK", description="Country code (e.g., 'PK', 'US')")
):
    """
    Get available video categories for a region.
    These are official YouTube categories.
    """
    try:
        categories = youtube_api.get_video_categories(region_code=country, api_key=api_key)
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

# Removed Pydantic models TrendsRequest, TrendsResponse as they were not strictly used for query params
# and response structure is now more dynamic/directly constructed.
# Consider re-adding with precise fields if strict validation is needed later.
