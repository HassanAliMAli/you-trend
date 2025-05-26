"""
YouTube API Integration Module for YouTrend

This module provides functions to interact with the YouTube Data API v3,
fetching channels, videos, and search results with quota optimization.
"""

import os
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

def get_youtube_client(api_key: str):
    """
    Initialize and return a YouTube API client using the provided api_key
    """
    if not api_key:
        raise ValueError("YouTube API key must be provided in the request.")
    return build('youtube', 'v3', developerKey=api_key)

def search_videos(api_key: str, query: str, max_results: int = 10, country: str = None, 
                 video_duration: str = None, order: str = 'viewCount') -> List[Dict]:
    """
    Search for YouTube videos based on query and filters
    
    Args:
        api_key: YouTube API key
        query: Search term
        max_results: Maximum number of results to return (default: 10, max: 50)
        country: Country code filter (e.g., 'US', 'GB', 'PK')
        video_duration: Duration filter ('short', 'medium', 'long')
        order: Sort order ('viewCount', 'relevance', 'rating')
        
    Returns:
        List of video resources with statistics and snippet information
    """
    # Limit max_results to 50 to optimize quota usage
    max_results = min(max_results, 50)
    
    youtube = get_youtube_client(api_key)
    
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
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return []

def get_channel_details(api_key: str, channel_ids: List[str]) -> List[Dict]:
    """
    Get detailed information about YouTube channels
    
    Args:
        api_key: YouTube API key
        channel_ids: List of YouTube channel IDs
        
    Returns:
        List of channel resources with statistics and snippet information
    """
    if not channel_ids:
        return []
    
    youtube = get_youtube_client(api_key)
    
    try:
        # Get channel details in a single batch request
        channels_response = youtube.channels().list(
            part='snippet,statistics,contentDetails',
            id=','.join(channel_ids)
        ).execute()
        
        return channels_response.get('items', [])
    
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return []

def get_trending_videos(api_key: str, region_code: str = 'PK', category_id: str = None, 
                        max_results: int = 10) -> List[Dict]:
    """
    Get trending videos for a specific region and optional category
    
    Args:
        api_key: YouTube API key
        region_code: ISO 3166-1 alpha-2 country code (default: 'PK' for Pakistan)
        category_id: YouTube video category ID
        max_results: Maximum number of results to return (default: 10, max: 50)
        
    Returns:
        List of trending video resources
    """
    max_results = min(max_results, 50)
    
    youtube = get_youtube_client(api_key)
    
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
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return []

def search_channels(api_key: str, query: str, max_results: int = 10, region_code: str = None) -> List[Dict]:
    """
    Search for YouTube channels based on query
    
    Args:
        api_key: YouTube API key
        query: Search term
        max_results: Maximum number of results to return (default: 10, max: 50)
        region_code: ISO 3166-1 alpha-2 country code
        
    Returns:
        List of channel resources with statistics and snippet information
    """
    max_results = min(max_results, 50)
    
    youtube = get_youtube_client(api_key)
    
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
        return get_channel_details(api_key, channel_ids)
    
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return []

def get_video_categories(api_key: str, region_code: str = 'PK') -> List[Dict]:
    """
    Get available video categories for a region
    
    Args:
        api_key: YouTube API key
        region_code: ISO 3166-1 alpha-2 country code (default: 'PK' for Pakistan)
        
    Returns:
        List of video category resources
    """
    youtube = get_youtube_client(api_key)
    
    try:
        categories_response = youtube.videoCategories().list(
            part='snippet',
            regionCode=region_code if region_code != 'Global' else 'US'
        ).execute()
        
        return categories_response.get('items', [])
    
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return []

def get_channel_videos(api_key: str, channel_id: str, max_results: int = 10, 
                      order: str = 'date') -> List[Dict]:
    """
    Get videos from a specific channel
    
    Args:
        api_key: YouTube API key
        channel_id: YouTube channel ID
        max_results: Maximum number of results to return (default: 10, max: 50)
        order: Sort order ('date', 'viewCount', 'title')
        
    Returns:
        List of video resources
    """
    max_results = min(max_results, 50)
    
    youtube = get_youtube_client(api_key)
    
    try:
        # Step 1: Search for videos from the channel
        search_response = youtube.search().list(
            part='id',
            channelId=channel_id,
            maxResults=max_results,
            order=order,
            type='video'
        ).execute()
        
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
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return []

def estimate_quota_cost(operation: str, items_count: int = 1) -> int:
    """
    Estimate API quota cost for various operations
    
    Args:
        operation: Operation type ('search', 'videos', 'channels')
        items_count: Number of items to process
        
    Returns:
        Estimated quota cost in units
    """
    # Quota costs per API call
    quota_costs = {
        'search': 100,
        'videos': 1,
        'channels': 1,
        'videoCategories': 1
    }
    
    # Calculate total cost (each item in a batch request costs units)
    base_cost = quota_costs.get(operation, 0)
    
    if operation == 'search':
        # Search is expensive - 100 units per request
        return base_cost
    else:
        # For list operations, cost is base + items
        return base_cost * items_count
