"""
Compare API Endpoints

This module provides API endpoints for comparing different YouTube niches,
allowing users to analyze multiple content categories.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from utils import youtube_api, data_processor

router = APIRouter(prefix="/api/compare", tags=["compare"])

# Request and response models
class CompareRequest(BaseModel):
    niches: List[str]
    country: str = "PK"  # Default to Pakistan
    max_results: int = 10
    order: str = "viewCount"

class CompareResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

@router.get("", response_model=CompareResponse)
async def compare_niches(
    niches: str = Query(..., description="Comma-separated list of niches to compare"),
    country: str = "PK",
    max_results: int = 10,
    order: str = "viewCount"
):
    """
    Compare different niches based on their YouTube metrics
    
    - **niches**: Comma-separated list of niches to compare (e.g., 'Gaming,Tech,Beauty')
    - **country**: Country code (e.g., 'PK', 'US')
    - **max_results**: Maximum number of results per niche (default: 10, max: 50)
    - **order**: Sort order for videos ('viewCount', 'relevance', 'rating', 'date')
    """
    try:
        # Parse niches from comma-separated string
        niche_list = [niche.strip() for niche in niches.split(',') if niche.strip()]
        
        if not niche_list:
            raise HTTPException(status_code=400, detail="No valid niches provided")
        
        # Limit number of niches to compare (to avoid excessive API calls)
        if len(niche_list) > 5:
            niche_list = niche_list[:5]
            
        # Gather videos for each niche
        niches_data = {}
        for niche in niche_list:
            videos = youtube_api.search_videos(
                query=niche,
                max_results=max_results,
                country=country,
                order=order
            )
            niches_data[niche] = videos
        
        # Compare niches
        comparison_results = data_processor.compare_niches(niches_data)
        
        return {
            "status": "success",
            "message": f"Successfully compared {len(niche_list)} niches",
            "data": comparison_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=CompareResponse)
async def get_niche_metrics(
    niche: str,
    country: str = "PK",
    max_results: int = 10
):
    """
    Get detailed metrics for a specific niche
    
    - **niche**: The niche to analyze (e.g., 'Gaming')
    - **country**: Country code (e.g., 'PK', 'US')
    - **max_results**: Maximum number of videos to analyze (default: 10, max: 50)
    """
    try:
        # Get videos for the niche
        videos = youtube_api.search_videos(
            query=niche,
            max_results=max_results,
            country=country,
            order="viewCount"
        )
        
        # Get trending videos in the country for comparison
        trending_videos = youtube_api.get_trending_videos(
            region_code=country,
            max_results=max_results
        )
        
        # Get channels related to the niche
        channels = youtube_api.search_channels(
            query=niche,
            max_results=max_results,
            region_code=country
        )
        
        # Analyze trends for the niche
        niche_analysis = data_processor.analyze_video_trends(videos)
        
        # Extract insights
        avg_views = 0
        avg_engagement = 0
        
        if videos:
            view_counts = [int(video.get('statistics', {}).get('viewCount', 0)) for video in videos]
            avg_views = sum(view_counts) / len(view_counts) if view_counts else 0
            
            engagement_rates = []
            for video in videos:
                stats = video.get('statistics', {})
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments = int(stats.get('commentCount', 0))
                
                if views > 0:
                    engagement_rates.append((likes + comments) / views)
                else:
                    engagement_rates.append(0)
            
            avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        
        return {
            "status": "success",
            "message": f"Successfully analyzed {niche} niche",
            "data": {
                "niche": niche,
                "metrics": {
                    "avg_views": avg_views,
                    "avg_engagement_rate": avg_engagement,
                    "video_count": len(videos)
                },
                "topics": niche_analysis.get('topics', []),
                "channels": channels[:5],  # Top 5 channels
                "video_ideas": niche_analysis.get('video_ideas', [])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
