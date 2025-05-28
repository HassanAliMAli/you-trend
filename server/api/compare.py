"""
Compare API Endpoints

This module provides API endpoints for comparing different YouTube niches,
allowing users to analyze multiple content categories.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

import utils.youtube_api as youtube_api
import utils.data_processor as data_processor
from utils.youtube_api import YouTubeApiError

# For user authentication (optional)
from server.utils import database, auth
from server.models.user import User as UserModel

router = APIRouter(prefix="/compare", tags=["compare"])

@router.get("", response_model=None)
async def compare_niches_endpoint(
    niches: str = Query(..., description="Comma-separated list of niches (keywords) to compare. Max 5."),
    country: str = Query("PK", description="Country code (e.g., 'PK', 'US')"),
    max_results_per_niche: int = Query(10, description="Max videos per niche for analysis (default:10, max:25)", ge=1, le=25),
    order: str = Query("viewCount", description="Sort order for videos ('viewCount', 'relevance', 'rating', 'date')"),
    published_after: Optional[str] = Query(None, description="Filter videos published after (YYYY-MM-DDTHH:MM:SSZ)"),
    published_before: Optional[str] = Query(None, description="Filter videos published before (YYYY-MM-DDTHH:MM:SSZ)"),
    language: Optional[str] = Query(None, description="Filter videos by language (ISO 639-1 code)"),
    api_key_query: Optional[str] = Query(None, description="Optional: YouTube Data API v3 key. Overrides user's or system key.", alias="api_key"),
    db: Session = Depends(database.get_db),
    current_user: Optional[UserModel] = Depends(auth.get_current_user_optional)
):
    """
    Compare different niches based on their YouTube metrics.
    Fetches videos for each niche and then runs comparative analysis.
    Prioritizes API key: query parameter > authenticated user's key > system .env key.
    """
    final_api_key_to_use = api_key_query
    if not final_api_key_to_use and current_user and current_user.youtube_api_key:
        final_api_key_to_use = current_user.youtube_api_key

    try:
        niche_list = [niche.strip() for niche in niches.split(',') if niche.strip()]
        
        if not niche_list:
            raise HTTPException(status_code=400, detail="No valid niches provided for comparison.")
        
        if len(niche_list) > 5:
            niche_list = niche_list[:5] # Silently cap at 5 for now
            
        niches_video_data: Dict[str, List[Dict[str, Any]]] = {}
        for niche_keyword in niche_list:
            videos = youtube_api.search_videos(
                query=niche_keyword,
                max_results=max_results_per_niche,
                country=country,
                order=order,
                published_after=published_after,
                published_before=published_before,
                relevance_language=language,
                api_key=final_api_key_to_use
            )
            niches_video_data[niche_keyword] = videos
        
        comparison_results = data_processor.compare_niches(niches_video_data)
        
        return {
            "status": "success",
            "message": f"Successfully processed comparison for {len(niche_list)} niches.",
            "data": comparison_results
        }
    except YouTubeApiError as yte:
        raise HTTPException(status_code=yte.status_code, detail=yte.detail)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during niche comparison: {str(e)}")
