"""
YouTube API Integration Module for YouTrend

This module provides functions to interact with the YouTube Data API v3,
fetching channels, videos, and search results with quota optimization.
"""

import os # Added import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

class YouTubeApiError(Exception):
    """Custom exception for YouTube API errors."""
    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)

def get_youtube_client(api_key: Optional[str] = None):
    """
    Initialize and return a YouTube API client using the provided api_key
    or the YOUTUBE_API_KEY environment variable.
    """
    resolved_api_key = api_key or os.getenv('YOUTUBE_API_KEY')
    if not resolved_api_key:
        raise ValueError("YouTube API key must be provided either as an argument or via YOUTUBE_API_KEY environment variable.")
    return build('youtube', 'v3', developerKey=resolved_api_key)

def search_videos(query: str, max_results: int = 10, country: str = None, 
                 video_duration: str = None, order: str = 'viewCount', api_key: Optional[str] = None) -> List[Dict]:
    """
    Search for YouTube videos based on query and filters
    
    Args:
        query: Search term
        max_results: Maximum number of results to return (default: 10, max: 50)
        country: Country code filter (e.g., 'US', 'GB', 'PK')
        video_duration: Duration filter ('short', 'medium', 'long')
        order: Sort order ('viewCount', 'relevance', 'rating')
        api_key: YouTube API key (optional, falls back to YOUTUBE_API_KEY env var)
        
    Returns:
        List of video resources with statistics and snippet information
    """
    max_results = min(max_results, 50)
    
    resolved_api_key = api_key or os.getenv('YOUTUBE_API_KEY')
    youtube = get_youtube_client(resolved_api_key)
    
    # Set up search parameters
    search_params = {
        'q': query,
        'type': 'video',
        'part': 'id',
        'maxResults': max_results,
        'order': order
    }
    
    # Add optional filters
    if country and country != 'Global':
        search_params['regionCode'] = country
    
    if video_duration and video_duration != 'Any Duration':
        # Map user-friendly duration to API values
        duration_mapping = {
            'Short (< 4 minutes)': 'short',
            'Medium (4-20 minutes)': 'medium',
            'Long (> 20 minutes)': 'long'
        }
        search_params['videoDuration'] = duration_mapping.get(video_duration, 'any')
    
    try:
        # Step 1: Search for video IDs
        search_response = youtube.search().list(**search_params).execute()
        
        # Extract video IDs
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        
        if not video_ids:
            return []
        
        # Step 2: Get detailed video info and statistics in a single batch request
        videos_response = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        ).execute()
        
        return videos_response.get('items', [])
    
    except HttpError as e:
        # print(f"An HTTP error {e.resp.status} occurred:\\n{e.content}")
        # return []
        raise YouTubeApiError(detail=f"YouTube API error: {e.resp.status} - {e.content}", status_code=e.resp.status)

def get_channel_details(channel_ids: List[str], api_key: Optional[str] = None) -> List[Dict]:
    """
    Get detailed information about YouTube channels
    
    Args:
        channel_ids: List of YouTube channel IDs
        api_key: YouTube API key (optional, falls back to YOUTUBE_API_KEY env var)
        
    Returns:
        List of channel resources with statistics and snippet information
    """
    if not channel_ids:
        return []
    
    resolved_api_key = api_key or os.getenv('YOUTUBE_API_KEY')
    youtube = get_youtube_client(resolved_api_key)
    
    try:
        # Get channel details in a single batch request
        channels_response = youtube.channels().list(
            part='snippet,statistics,contentDetails',
            id=','.join(channel_ids)
        ).execute()
        
        return channels_response.get('items', [])
    
    except HttpError as e:
        # print(f"An HTTP error {e.resp.status} occurred:\\n{e.content}")
        # return []
        raise YouTubeApiError(detail=f"YouTube API error: {e.resp.status} - {e.content}", status_code=e.resp.status)

def get_trending_videos(region_code: str = 'PK', category_id: str = None, 
                        max_results: int = 10, api_key: Optional[str] = None) -> List[Dict]:
    """
    Get trending videos for a specific region and optional category
    
    Args:
        region_code: ISO 3166-1 alpha-2 country code (default: 'PK' for Pakistan)
        category_id: YouTube video category ID
        max_results: Maximum number of results to return (default: 10, max: 50)
        api_key: YouTube API key (optional, falls back to YOUTUBE_API_KEY env var)
        
    Returns:
        List of trending video resources
    """
    max_results = min(max_results, 50)
    
    resolved_api_key = api_key or os.getenv('YOUTUBE_API_KEY')
    youtube = get_youtube_client(resolved_api_key)
    
    # Set up trending request parameters
    trending_params = {
        'part': 'snippet,statistics',
        'chart': 'mostPopular',
        'regionCode': region_code if region_code != 'Global' else 'US',
        'maxResults': max_results
    }
    
    # Add optional category filter
    if category_id:
        trending_params['videoCategoryId'] = category_id
    
    try:
        trending_response = youtube.videos().list(**trending_params).execute()
        return trending_response.get('items', [])
    
    except HttpError as e:
        # print(f"An HTTP error {e.resp.status} occurred:\\n{e.content}")
        # return []
        raise YouTubeApiError(detail=f"YouTube API error: {e.resp.status} - {e.content}", status_code=e.resp.status)

def search_channels(query: str, max_results: int = 10, region_code: str = None, api_key: Optional[str] = None) -> List[Dict]:
    """
    Search for YouTube channels based on query
    
    Args:
        query: Search term
        max_results: Maximum number of results to return (default: 10, max: 50)
        region_code: ISO 3166-1 alpha-2 country code
        api_key: YouTube API key (optional, falls back to YOUTUBE_API_KEY env var)
        
    Returns:
        List of channel resources with statistics and snippet information
    """
    max_results = min(max_results, 50)
    
    resolved_api_key = api_key or os.getenv('YOUTUBE_API_KEY')
    youtube = get_youtube_client(resolved_api_key)
    
    # Set up search parameters
    search_params = {
        'q': query,
        'type': 'channel',
        'part': 'id',
        'maxResults': max_results
    }
    
    # Add optional region filter
    if region_code and region_code != 'Global':
        search_params['regionCode'] = region_code
    
    try:
        # Step 1: Search for channel IDs
        search_response = youtube.search().list(**search_params).execute()
        
        # Extract channel IDs
        channel_ids = [item['id']['channelId'] for item in search_response.get('items', [])]
        
        if not channel_ids:
            return []
        
        # Step 2: Get detailed channel info
        return get_channel_details(channel_ids, resolved_api_key)
    
    except HttpError as e:
        # print(f"An HTTP error {e.resp.status} occurred:\\n{e.content}")
        # return []
        raise YouTubeApiError(detail=f"YouTube API error: {e.resp.status} - {e.content}", status_code=e.resp.status)

def get_video_categories(region_code: str = 'PK', api_key: Optional[str] = None) -> List[Dict]:
    """
    Get available video categories for a region
    
    Args:
        region_code: ISO 3166-1 alpha-2 country code (default: 'PK' for Pakistan)
        api_key: YouTube API key (optional, falls back to YOUTUBE_API_KEY env var)
        
    Returns:
        List of video category resources
    """
    resolved_api_key = api_key or os.getenv('YOUTUBE_API_KEY')
    youtube = get_youtube_client(resolved_api_key)
    
    try:
        categories_response = youtube.videoCategories().list(
            part='snippet',
            regionCode=region_code if region_code != 'Global' else 'US'
        ).execute()
        
        return categories_response.get('items', [])
    
    except HttpError as e:
        # print(f"An HTTP error {e.resp.status} occurred:\\n{e.content}")
        # return []
        raise YouTubeApiError(detail=f"YouTube API error: {e.resp.status} - {e.content}", status_code=e.resp.status)

def get_channel_videos(channel_id: str, max_results: int = 10, 
                      order: str = 'date', api_key: Optional[str] = None) -> List[Dict]:
    """
    Get videos from a specific channel
    
    Args:
        channel_id: YouTube channel ID
        max_results: Maximum number of results to return (default: 10, max: 50)
        order: Sort order ('date', 'viewCount', 'title')
        api_key: YouTube API key (optional, falls back to YOUTUBE_API_KEY env var)
        
    Returns:
        List of video resources
    """
    max_results = min(max_results, 50)
    
    resolved_api_key = api_key or os.getenv('YOUTUBE_API_KEY')
    youtube = get_youtube_client(resolved_api_key)
    
    try:
        # Step 1: Search for videos from the channel
        search_params = {
            'channelId': channel_id,
            'type': 'video',
            'part': 'id',
            'order': order,
            'maxResults': max_results
        }
        
        search_response = youtube.search().list(**search_params).execute()
        
        # Extract video IDs
        video_ids = [item['id']['videoId'] for item in search_response.get('items', []) if item.get('id', {}).get('videoId')]
        
        if not video_ids:
            return []
        
        # Step 2: Get detailed video info and statistics in a single batch request
        videos_response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(video_ids)
        ).execute()
        
        return videos_response.get('items', [])
    
    except HttpError as e:
        # print(f"An HTTP error {e.resp.status} occurred:\\n{e.content}")
        # return []
        raise YouTubeApiError(detail=f"Failed to get videos for channel_id {channel_id}: {e.resp.status} - {e.content}", status_code=e.resp.status)

def get_video_details_by_id(video_ids: List[str], api_key: Optional[str] = None) -> List[Dict]:
    """
    Get details for a list of video IDs.
    Args:
        video_ids: A list of video IDs.
        api_key: YouTube API key (optional, falls back to YOUTUBE_API_KEY env var)
    """
    if not video_ids:
        return []
    
    resolved_api_key = api_key or os.getenv('YOUTUBE_API_KEY')
    youtube = get_youtube_client(resolved_api_key)

    try:
        videos_response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(video_ids)
        ).execute()
        return videos_response.get('items', [])
    except HttpError as e:
        raise YouTubeApiError(detail=f"Failed to get video details: {e.resp.status} - {e.content}", status_code=e.resp.status)
