"""
Redis Caching Module for YouTrend

This module provides caching functionality for YouTube API results
to minimize quota usage and improve response times.
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, List, Any, Optional, Union, Callable
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "development_secret_key")

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Redis connection
try:
    redis_client = redis.from_url(REDIS_URL)
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
    logging.info("Successfully connected to Redis.")
except Exception as e:
    logging.warning(f"Redis connection failed: {e}. Running in non-cached mode.")
    REDIS_AVAILABLE = False

# Cache settings
DEFAULT_TTL = 3600  # 1 hour in seconds
QUOTA_KEY = "youtube_api_quota"
QUOTA_LIMIT = 10000  # Daily quota limit for YouTube API
QUOTA_WARNING_THRESHOLD = 0.8  # 80% of quota limit

def generate_cache_key(prefix: str, params: Dict[str, Any]) -> str:
    """
    Generate a unique cache key based on API call parameters
    
    Args:
        prefix: Prefix for the cache key
        params: Dictionary of parameters to include in the key
        
    Returns:
        Unique cache key string
    """
    # Convert params to a stable string representation
    param_str = json.dumps(params, sort_keys=True)
    
    # Generate hash of the parameters
    params_hash = hashlib.md5(param_str.encode()).hexdigest()
    
    # Return prefixed key
    return f"youtrend:{prefix}:{params_hash}"

def get_cached_result(key: str) -> Optional[Any]:
    """
    Get result from cache if available
    
    Args:
        key: Cache key to retrieve
        
    Returns:
        Cached data if available, None otherwise
    """
    if not REDIS_AVAILABLE:
        return None
    
    try:
        cached_data = redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    except Exception as e:
        logging.warning(f"Error retrieving from cache (key: {key}): {e}")
        return None

def set_cached_result(key: str, data: Any, ttl: int = DEFAULT_TTL) -> bool:
    """
    Store result in cache
    
    Args:
        key: Cache key to store
        data: Data to cache
        ttl: Time-to-live in seconds (default: 1 hour)
        
    Returns:
        True if successful, False otherwise
    """
    if not REDIS_AVAILABLE:
        return False
    
    try:
        json_data = json.dumps(data)
        redis_client.setex(key, ttl, json_data)
        return True
    except redis.RedisError as e:
        logging.error(f"Redis error setting cache key {key}: {e}")
        return False
    except TypeError as e:  # Handle JSON serialization errors
        logging.error(f"Could not serialize data for cache key {key}: {e}")
        return False

def track_quota_usage(cost: int) -> Dict[str, Any]:
    """
    Track YouTube API quota usage
    
    Args:
        cost: Cost in quota units for the current operation
        
    Returns:
        Dictionary with quota usage statistics
    """
    if not REDIS_AVAILABLE:
        return {
            "tracked": False,
            "usage": 0,
            "limit": QUOTA_LIMIT,
            "percentage": 0,
            "warning": False
        }
    
    try:
        # Get current usage
        current_usage = redis_client.get(QUOTA_KEY)
        
        if current_usage:
            current_usage = int(current_usage)
        else:
            # Initialize quota tracking for the day
            current_usage = 0
            # Set expiration to end of day (UTC)
            seconds_until_midnight = 86400 - (int(time.time()) % 86400)
            redis_client.setex(QUOTA_KEY, seconds_until_midnight, str(current_usage))
        
        # Increment usage
        new_usage = current_usage + cost
        redis_client.set(QUOTA_KEY, str(new_usage))
        
        # Calculate percentage and warning status
        percentage = new_usage / QUOTA_LIMIT
        warning = percentage >= QUOTA_WARNING_THRESHOLD
        
        return {
            "tracked": True,
            "usage": new_usage,
            "limit": QUOTA_LIMIT,
            "percentage": percentage,
            "warning": warning
        }
    except Exception as e:
        logging.error(f"Error tracking quota usage: {e}")
        return {
            "tracked": False,
            "error": str(e),
            "usage": 0,
            "limit": QUOTA_LIMIT,
            "percentage": 0,
            "warning": False
        }

def cached_api_call(
    func: Callable,
    prefix: str,
    params: Dict[str, Any],
    quota_cost: int = 1,
    ttl: int = DEFAULT_TTL
) -> Any:
    """
    Wrapper for API calls with caching
    
    Args:
        func: API function to call
        prefix: Prefix for cache key
        params: Parameters for the API call
        quota_cost: Cost in quota units for the API call
        ttl: Time-to-live in seconds for cached results
        
    Returns:
        Result from API call or cache
    """
    # Generate cache key
    cache_key = generate_cache_key(prefix, params)
    
    # Try to get from cache
    cached_result = get_cached_result(cache_key)
    if cached_result is not None:
        return {
            "data": cached_result,
            "cached": True,
            "quota": {
                "used": 0,
                "tracked": False
            }
        }
    
    # Track quota usage
    quota_info = track_quota_usage(quota_cost)
    
    # Perform API call
    result = func(**params)
    
    # Cache result
    cache_success = set_cached_result(cache_key, result, ttl)
    
    return {
        "data": result,
        "cached": False,
        "cache_stored": cache_success,
        "quota": quota_info
    }

def clear_cache(prefix: Optional[str] = None) -> int:
    """
    Clear cache entries
    
    Args:
        prefix: Optional prefix to clear only specific keys
        
    Returns:
        Number of keys cleared
    """
    if not REDIS_AVAILABLE:
        return 0
    
    try:
        if prefix:
            # Clear keys with specific prefix
            pattern = f"youtrend:{prefix}:*"
            keys_to_delete = [key.decode('utf-8') for key in redis_client.scan_iter(match=pattern)]
            if keys_to_delete:
                return redis_client.delete(*keys_to_delete)
            return 0
        else:
            # Clear all YouTrend keys (scan_iter is safer than keys() for large DBs)
            pattern = "youtrend:*"
            keys_to_delete = [key.decode('utf-8') for key in redis_client.scan_iter(match=pattern)]
            if keys_to_delete:
                return redis_client.delete(*keys_to_delete)
            return 0
    except Exception as e:
        logging.error(f"Error clearing cache: {e}")
        return 0

def get_quota_usage() -> Dict[str, Any]:
    """
    Get current YouTube API quota usage
    
    Returns:
        Dictionary with quota usage statistics
    """
    if not REDIS_AVAILABLE:
        return {
            "tracked": False,
            "usage": 0,
            "limit": QUOTA_LIMIT,
            "percentage": 0,
            "warning": False
        }
    
    try:
        # Get current usage
        current_usage = redis_client.get(QUOTA_KEY)
        
        if current_usage:
            current_usage = int(current_usage)
        else:
            current_usage = 0
        
        # Calculate percentage and warning status
        percentage = current_usage / QUOTA_LIMIT
        warning = percentage >= QUOTA_WARNING_THRESHOLD
        
        return {
            "tracked": True,
            "usage": current_usage,
            "limit": QUOTA_LIMIT,
            "percentage": percentage,
            "warning": warning,
            "remaining": QUOTA_LIMIT - current_usage
        }
    except Exception as e:
        logging.error(f"Error getting quota usage: {e}")
        return {
            "tracked": False,
            "error": str(e),
            "usage": 0,
            "limit": QUOTA_LIMIT,
            "percentage": 0,
            "warning": False,
            "remaining": QUOTA_LIMIT
        }

def invalidate_cache_by_prefix(prefix: str):
    """
    Invalidate cache entries by prefix
    
    Args:
        prefix: Prefix to invalidate cache entries
    """
    if not REDIS_AVAILABLE:
        return
    try:
        # Clear keys with specific prefix
        pattern = f"youtrend:{prefix}:*"
        keys_to_delete = [key.decode('utf-8') for key in redis_client.scan_iter(match=pattern)]
        if keys_to_delete:
            redis_client.delete(*keys_to_delete)
    except Exception as e:
        logging.error(f"Error invalidating cache by prefix {prefix}: {e}")
