"""
Trends API Endpoints

This module provides API endpoints for analyzing YouTube trends,
including video search, trending videos, and trend analysis.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from utils import youtube_api, data_processor
from utils.youtube_api import YouTubeApiError

router = APIRouter(prefix="/trends", tags=["trends"])

# Request and response models
class TrendsRequest(BaseModel):
    query: str = ""
    category: Optional[str] = None
    country: str = "PK"  # Default to Pakistan
    duration: Optional[str] = None
    max_results: int = 10
    order: str = "viewCount"

class TrendsResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

@router.get("", response_model=TrendsResponse)
async def get_trends(
    api_key: str = Query(..., description="YouTube Data API v3 key (required)"),
    query: str = "",
    category: Optional[str] = None,
    country: str = "PK",
    duration: Optional[str] = None,
    max_results: int = 10,
    order: str = "viewCount"
):
    """
    Get trending videos and analysis based on search parameters
    
    - **query**: Search term for videos
    - **category**: Video category ID
    - **country**: Country code (e.g., 'PK', 'US')
    - **duration**: Duration filter ('Short (< 4 minutes)', 'Medium (4-20 minutes)', 'Long (> 20 minutes)')
    - **max_results**: Maximum number of results to return (default: 10, max: 50)
    - **order**: Sort order ('viewCount', 'relevance', 'rating', 'date')
    """
    if not api_key:
        raise HTTPException(status_code=400, detail="YouTube API key is required.")
    try:
        # 1. Fetch videos based on query or trending
        videos = []
        if query:
            # Search videos based on query
            videos = youtube_api.search_videos(
                api_key=api_key,
                query=query,
                max_results=max_results,
                country=country,
                video_duration=duration,
                order=order
            )
        else:
            # Get trending videos
            videos = youtube_api.get_trending_videos(
                api_key=api_key,
                region_code=country,
                category_id=category,
                max_results=max_results
            )
        
        # 2. Perform trend analysis
        trend_analysis = data_processor.analyze_video_trends(videos)
        
        # 3. Extract videos, topics, and video ideas from trend analysis
        ranked_videos = trend_analysis.get('ranked_videos', [])
        topics = trend_analysis.get('topics', [])
        video_ideas = trend_analysis.get('video_ideas', [])
        metadata_insights = trend_analysis.get('metadata_insights', {})
        
        return {
            "status": "success",
            "message": f"Found {len(ranked_videos)} videos matching your criteria",
            "data": {
                "videos": ranked_videos,
                "topics": topics,
                "ideas": video_ideas,
                "insights": metadata_insights
            }
        }
        
    except YouTubeApiError as yte:
        raise HTTPException(status_code=yte.status_code, detail=yte.detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/channels", response_model=TrendsResponse)
async def get_trending_channels(
    api_key: str = Query(..., description="YouTube Data API v3 key (required)"),
    query: str = "",
    country: str = "PK",
    max_results: int = 10
):
    """
    Get trending channels based on search parameters
    
    - **query**: Search term for channels
    - **country**: Country code (e.g., 'PK', 'US')
    - **max_results**: Maximum number of results to return (default: 10, max: 50)
    """
    if not api_key:
        raise HTTPException(status_code=400, detail="YouTube API key is required.")
    try:
        # 1. Search for channels
        channels = youtube_api.search_channels(
            api_key=api_key,
            query=query,
            max_results=max_results,
            region_code=country
        )
        
        # 2. Get videos for the top channels to perform analysis
        videos_by_channel = {}
        for channel in channels[:5]:  # Limit to top 5 channels to avoid quota issues
            channel_id = channel.get('id')
            if channel_id:
                videos = youtube_api.get_channel_videos(
                    api_key=api_key,
                    channel_id=channel_id,
                    max_results=10,  # Get 10 videos per channel
                    order="viewCount"  # Get most viewed videos
                )
                videos_by_channel[channel_id] = videos
        
        # 3. Perform channel trend analysis
        channel_analysis = data_processor.analyze_channel_trends(channels, videos_by_channel)
        
        # 4. Extract analysis results
        ranked_channels = channel_analysis.get('ranked_channels', [])
        subscriber_distribution = channel_analysis.get('subscriber_distribution', {})
        posting_frequency = channel_analysis.get('posting_frequency', {})
        
        return {
            "status": "success",
            "message": f"Found {len(ranked_channels)} channels matching your criteria",
            "data": {
                "channels": ranked_channels,
                "subscriber_distribution": subscriber_distribution,
                "posting_frequency": posting_frequency
            }
        }
        
    except YouTubeApiError as yte:
        raise HTTPException(status_code=yte.status_code, detail=yte.detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/categories", response_model=TrendsResponse)
async def get_video_categories_endpoint(
    api_key: str = Query(..., description="YouTube Data API v3 key (required)"),
    country: str = "PK"
):
    """
    Get available video categories for a region
    
    - **country**: Country code (e.g., 'PK', 'US')
    """
    if not api_key:
        raise HTTPException(status_code=400, detail="YouTube API key is required.")
    try:
        categories = youtube_api.get_video_categories(api_key=api_key, region_code=country)
        
        return {
            "status": "success",
            "message": f"Found {len(categories)} video categories",
            "data": {
                "categories": categories
            }
        }
    except YouTubeApiError as yte:
        raise HTTPException(status_code=yte.status_code, detail=yte.detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
