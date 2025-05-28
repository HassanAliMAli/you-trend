"""
Data Processing Module for YouTrend

This module analyzes YouTube data to identify trends, calculate metrics,
and generate insights for channels, videos, and topics.
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter, defaultdict
import pandas as pd
import numpy as np
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _parse_duration_to_seconds(duration_str: Optional[str]) -> int:
    """Helper function to parse ISO 8601 duration to seconds."""
    if not duration_str:
        return 0
    
    # Regex to parse ISO 8601 durations
    # Handles PT<hours>H<minutes>M<seconds>S format
    match = re.match(r'PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?', duration_str)
    if not match:
        return 0
    
    parts = match.groupdict()
    hours = int(parts['hours'] or 0)
    minutes = int(parts['minutes'] or 0)
    seconds = int(parts['seconds'] or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def calculate_video_score(video: Dict[str, Any]) -> float:
    """
    Calculate a weighted score for a video based on views, engagement, and recency
    
    Weight distribution:
    - 40% views
    - 40% engagement rate (likes + comments / views)
    - 20% recency
    
    Args:
        video: Video resource from YouTube API
        
    Returns:
        Weighted score (higher is better)
    """
    try:
        # Extract metrics
        statistics = video.get('statistics', {})
        snippet = video.get('snippet', {})
        
        view_count = int(statistics.get('viewCount', 0))
        like_count = int(statistics.get('likeCount', 0))
        comment_count = int(statistics.get('commentCount', 0))
        
        # Calculate engagement rate (likes + comments / views)
        engagement_rate = 0.0 # ensure float
        if view_count > 0:
            engagement_rate = (like_count + comment_count) / view_count
        
        # Calculate recency score (newer is better)
        published_at_str = snippet.get('publishedAt', '')
        recency_score = 0.0 # ensure float
        if published_at_str:
            try:
                # Handle potential timezone issues by ensuring consistent offset
                if 'Z' in published_at_str:
                    published_date = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                elif '+' in published_at_str or '-' in published_at_str[10:]: # Check for existing offset
                    published_date = datetime.fromisoformat(published_at_str)
                else: # Assume UTC if no timezone info and not 'Z'
                     published_date = datetime.fromisoformat(published_at_str + '+00:00')

                days_since_published = (datetime.now(published_date.tzinfo) - published_date).days
                recency_score = 1.0 / (1.0 + days_since_published) if days_since_published >= 0 else 0.0
            except ValueError as ve:
                logging.warning(f"Could not parse date '{published_at_str}' for video {video.get('id', 'unknown')}: {ve}")
                recency_score = 0.0
        
        # Calculate weighted score
        # Normalize view count (logarithmic scale)
        # Clamp normalized_views to avoid issues with very low/zero views if log1p is not enough
        normalized_views = np.log1p(view_count) / np.log1p(1_000_000_000) # Normalize against 1B views as a high benchmark
        normalized_views = min(max(normalized_views, 0.0), 1.0) # Ensure it's between 0 and 1

        # Apply weights
        weighted_score = (
            0.4 * normalized_views +
            0.4 * min(engagement_rate, 1.0) + 
            0.2 * recency_score
        )
        
        return round(weighted_score, 4) # Return rounded score
    
    except Exception as e:
        logging.error(f"Error calculating video score for video ID {video.get('id', 'unknown')}: {e}", exc_info=True)
        return 0.0

def calculate_channel_score(channel: Dict[str, Any], videos: List[Dict[str, Any]] = None) -> float:
    """
    Calculate a weighted score for a channel based on subscribers, average views, and posting frequency
    
    Weight distribution:
    - 30% subscriber count
    - 40% average video views
    - 30% posting frequency
    
    Args:
        channel: Channel resource from YouTube API
        videos: List of video resources for the channel (optional for avg_views and frequency)
        
    Returns:
        Weighted score (higher is better)
    """
    try:
        statistics = channel.get('statistics', {})
        subscriber_count = int(statistics.get('subscriberCount', 0))
        
        avg_views = 0.0
        posting_frequency = 0.0 # Videos per month
        
        if videos:
            view_counts = [int(v.get('statistics', {}).get('viewCount', 0)) for v in videos if v.get('statistics')]
            if view_counts:
                avg_views = sum(view_counts) / len(view_counts)
            
            publish_dates_str = [v.get('snippet', {}).get('publishedAt') for v in videos if v.get('snippet', {}).get('publishedAt')]
            publish_dates = []
            for date_str in publish_dates_str:
                try:
                    if 'Z' in date_str:
                        publish_dates.append(datetime.fromisoformat(date_str.replace('Z', '+00:00')))
                    elif '+' in date_str or '-' in date_str[10:]:
                         publish_dates.append(datetime.fromisoformat(date_str))
                    else:
                        publish_dates.append(datetime.fromisoformat(date_str + '+00:00'))
                except ValueError:
                    continue # Skip unparseable dates

            if len(publish_dates) >= 2:
                publish_dates.sort()
                days_span = (publish_dates[-1] - publish_dates[0]).days
                if days_span > 0:
                    videos_per_day = len(publish_dates) / days_span
                    posting_frequency = videos_per_day * 30.0  # Convert to monthly
        else: # Fallback if no videos provided, try to use channel total video count and creation date (if available)
            # This part is a rough estimation if channel creation date was available.
            # For now, if no videos, avg_views and posting_frequency remain 0.
            pass

        # Normalize metrics
        normalized_subscribers = np.log1p(subscriber_count) / np.log1p(200_000_000) # Normalize against 200M (MrBeast as benchmark)
        normalized_subscribers = min(max(normalized_subscribers, 0.0), 1.0)

        normalized_avg_views = np.log1p(avg_views) / np.log1p(50_000_000) # Normalize against 50M avg views
        normalized_avg_views = min(max(normalized_avg_views, 0.0), 1.0)
        
        # Normalize posting frequency (e.g., 0-30 videos/month maps to 0-1)
        normalized_frequency = min(posting_frequency / 30.0, 1.0) 
        normalized_frequency = max(normalized_frequency, 0.0)
        
        weighted_score = (
            0.3 * normalized_subscribers +
            0.4 * normalized_avg_views +
            0.3 * normalized_frequency
        )
        
        return round(weighted_score, 4)
    
    except Exception as e:
        logging.error(f"Error calculating channel score for channel ID {channel.get('id', 'unknown')}: {e}", exc_info=True)
        return 0.0

def extract_topics_from_videos(videos: List[Dict[str, Any]], top_n: int = 20) -> List[Dict[str, Any]]:
    """
    Extract trending topics/formats from videos, ranked by aggregated performance (views, engagement).
    
    Args:
        videos: List of video resources from YouTube API.
        top_n: Number of top topics to return.
        
    Returns:
        List of topic objects with name, aggregated_views, aggregated_engagement_score, video_count.
    """
    if not videos:
        return []

    common_keywords_patterns = [
        # General How-to & Guides
        r'how\s+to', r'tutorial', r'guide', r'explained', r'for\s+beginners',
        # Reviews & Comparisons
        r'review', r'vs\.?|versus', r'comparison',
        # Lists & Tops
        r'top\s*\d+', r'best\s*\d*', r'worst\s*\d*', r'\d+\s*tips', r'\d+\s*ways',
        # Reactions & Challenges
        r'react(?:ion)?s?', r'challenge',
        # Specific Content Types
        r'interview', r'gameplay', r'walkthrough', r'highlights?', r'montage',
        r'podcast', r'news', r'update', r'vlog', r'unboxing', r'diy',
        # Common adjectives often indicating type
        r'easy', r'quick', r'simple', r'ultimate', r'complete'
    ]
    
    # Stores {topic_name: {'total_views': X, 'total_engagement_score': Y, 'video_ids': set()}}
    topic_performance = defaultdict(lambda: {'total_views': 0, 'total_engagement_score': 0.0, 'video_ids': set()})

    for video in videos:
        title = video.get('snippet', {}).get('title', '').lower()
        # video_tags = [tag.lower() for tag in video.get('snippet', {}).get('tags', []) if tag] # Lowercase tags
        
        view_count = int(video.get('statistics', {}).get('viewCount', 0))
        like_count = int(video.get('statistics', {}).get('likeCount', 0))
        comment_count = int(video.get('statistics', {}).get('commentCount', 0))
        
        engagement_score_component = 0.0
        if view_count > 0:
            # Using a simple engagement sum (likes+comments) for aggregation,
            # as engagement rate * views would just be likes+comments.
            # Or, we can use the engagement_rate part of video_score.
            # Let's use likes + comments as a proxy for engagement magnitude.
            engagement_score_component = like_count + comment_count


        found_topics_for_video = set()

        # Extract from titles using regex
        for pattern in common_keywords_patterns:
            try:
                matches = re.findall(pattern, title)
                for match_text in matches:
                    # Normalize match_text (e.g., "top 10" vs "top 5")
                    normalized_topic = re.sub(r'\d+', 'N', match_text).strip() # Replace numbers with 'N'
                    if len(normalized_topic) > 2 and normalized_topic not in found_topics_for_video: # Avoid too short or duplicate topics for the same video
                        topic_performance[normalized_topic]['total_views'] += view_count
                        topic_performance[normalized_topic]['total_engagement_score'] += engagement_score_component
                        topic_performance[normalized_topic]['video_ids'].add(video['id'])
                        found_topics_for_video.add(normalized_topic)
            except re.error as re_err:
                logging.warning(f"Regex error with pattern '{pattern}' on title '{title}': {re_err}")


        # Consider adding topic extraction from tags too, if desired, with similar logic
        # For now, focusing on title-based keyword/format extraction
        # for tag in video_tags:
        #     if len(tag) > 3 and len(tag.split()) <= 3: # Simple filter for tags
        #          # Check if tag itself matches any known patterns or is a good standalone topic
        #         topic_performance[tag]['total_views'] += view_count
        #         topic_performance[tag]['total_engagement_score'] += engagement_score_component
        #         topic_performance[tag]['video_ids'].add(video['id'])


    # Prepare ranked list
    ranked_topics = []
    for name, data in topic_performance.items():
        if not data['video_ids']: continue # Should not happen if logic is correct
        avg_views_per_video = data['total_views'] / len(data['video_ids'])
        avg_engagement_score_per_video = data['total_engagement_score'] / len(data['video_ids'])
        
        # Composite score for ranking: e.g., log of views + log of engagement
        # Taking log1p to handle zeros. Multiplying by video_count to give some weight to more represented topics.
        # This ranking heuristic can be tuned.
        composite_score = (np.log1p(avg_views_per_video) + np.log1p(avg_engagement_score_per_video)) * np.log1p(len(data['video_ids']))

        ranked_topics.append({
            "name": name,
            "aggregated_views": data['total_views'],
            "avg_views_per_video": round(avg_views_per_video),
            "avg_engagement_score_per_video": round(avg_engagement_score_per_video, 2), # This is sum of L+C, not rate
            "video_count": len(data['video_ids']),
            "composite_score": composite_score 
        })

    # Sort by the composite score, then by video_count as a tie-breaker
    ranked_topics.sort(key=lambda x: (x["composite_score"], x["video_count"]), reverse=True)
    
    return ranked_topics[:top_n]

def generate_video_ideas(topics: List[Dict[str, Any]], videos: List[Dict[str, Any]], top_n_ideas: int = 10) -> List[Dict[str, str]]:
    """
    Generate actionable video ideas based on trending topics and top-performing videos.
    
    Args:
        topics: List of topic objects (from extract_topics_from_videos, now performance-ranked).
        videos: List of video resources from YouTube API.
        top_n_ideas: Number of video ideas to generate.
        
    Returns:
        List of video idea dictionaries, including title, description, and estimated potential.
    """
    if not topics or not videos:
        return []

    video_ideas = []
    
    # Sort videos by their score to easily pick high-performers
    sorted_videos = sorted(videos, key=lambda v: calculate_video_score(v), reverse=True)
    
    # Consider top N topics for generating ideas
    for topic_data in topics[:max(top_n_ideas, 5)]: # Use at least top 5 topics if top_n_ideas is small
        topic_name = topic_data.get("name", "Unknown Topic")
        
        # Find a high-performing video that might relate to this topic or general high performers
        # This is a simple heuristic: try to find a video that mentions topic or pick a general top video
        relevant_video_example = None
        for video in sorted_videos[:10]: # Look among top 10 videos
            if topic_name.lower() in video.get('snippet', {}).get('title', '').lower():
                relevant_video_example = video
                break
        if not relevant_video_example and sorted_videos:
            relevant_video_example = sorted_videos[0] # Fallback to the absolute top video

        if relevant_video_example:
            example_title = relevant_video_example.get('snippet', {}).get('title', 'Example Title')
            # example_tags = relevant_video_example.get('snippet', {}).get('tags', [])
            # example_duration_iso = relevant_video_example.get('contentDetails', {}).get('duration')
            # example_duration_seconds = _parse_duration_to_seconds(example_duration_iso)
            # duration_suggestion = f"{example_duration_seconds // 60}-{example_duration_seconds // 60 + 2} minutes" if example_duration_seconds else "optimal"


            idea_title = f"\"{topic_name.capitalize()}\": Inspired by \"{example_title[:50]}...\""
            
            description_parts = [
                f"Create a video about '{topic_name}'. This topic is currently performing well.",
                f"Consider a style similar to successful videos like '{example_title[:50]}...'.",
            ]
            
            # Estimate potential based on topic's aggregated performance
            # This is a qualitative assessment
            avg_topic_views = topic_data.get("avg_views_per_video", 0)
            view_potential = "Medium"
            if avg_topic_views > 100000: # Example thresholds
                view_potential = "High"
            elif avg_topic_views < 10000:
                view_potential = "Low to Medium"

            competition_level = "Medium" # Placeholder, real competition analysis is complex
            if topic_data.get("video_count", 0) > 10 and avg_topic_views > 50000 : # Many videos but still good views
                competition_level = "High"
            elif topic_data.get("video_count", 0) < 5:
                 competition_level = "Low"


            description_parts.append(f"Estimated Potential: {view_potential} views, {competition_level} competition.")
            description_parts.append("Focus on a catchy thumbnail and clear, engaging content.")


            video_ideas.append({
                "title": idea_title,
                "description": " ".join(description_parts),
                "topic": topic_name,
                "estimated_view_potential": view_potential, # Added
                "estimated_competition": competition_level, # Added
                "format_suggestion": f"Adapt content from '{topic_name}' format.", # Generic
                "thumbnail_tip": "Use bright colors, clear text, and expressive faces/objects if relevant.", # Generic
            })
            if len(video_ideas) >= top_n_ideas:
                break
        else: # No relevant video example found, generate a more generic idea for the topic
             video_ideas.append({
                "title": f"New Video Idea: {topic_name.capitalize()}",
                "description": f"Explore the topic of '{topic_name}'. This is an emerging area of interest.",
                "topic": topic_name,
                "estimated_view_potential": "Medium", 
                "estimated_competition": "Medium", 
                "format_suggestion": "Research common formats for this type of content.",
                "thumbnail_tip": "Ensure your thumbnail is high-resolution and stands out.",
            })
             if len(video_ideas) >= top_n_ideas:
                break


    return video_ideas[:top_n_ideas]

def suggest_related_niches(
    base_niche_videos: List[Dict[str, Any]], 
    all_available_videos_by_niche: Dict[str, List[Dict[str, Any]]],
    base_niche_name: str,
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Suggest related niches based on keyword overlap in titles/tags and shared channel viewership.
    This is a simplified version focusing on keyword overlap in video titles for now.
    
    Args:
        base_niche_videos: List of videos for the primary niche being analyzed.
        all_available_videos_by_niche: A dict where keys are niche names and values are lists of videos for those niches.
        base_niche_name: The name of the base niche.
        top_n: Number of related niches to suggest.
        
    Returns:
        List of suggested niche dicts with name and a relevance_score.
    """
    if not base_niche_videos:
        return []

    base_niche_keywords = Counter()
    for video in base_niche_videos:
        title_words = re.findall(r'\w+', video.get('snippet', {}).get('title', '').lower())
        for word in title_words:
            if len(word) > 3: # Basic filter for word length
                base_niche_keywords[word] += 1
    
    # Consider only reasonably common keywords from the base niche
    significant_base_keywords = {kw for kw, count in base_niche_keywords.most_common(50) if count > 1}

    relatedness_scores = defaultdict(float)

    for niche_name, niche_videos in all_available_videos_by_niche.items():
        if niche_name == base_niche_name or not niche_videos:
            continue

        current_niche_keywords = Counter()
        for video in niche_videos:
            title_words = re.findall(r'\w+', video.get('snippet', {}).get('title', '').lower())
            for word in title_words:
                if len(word) > 3:
                     current_niche_keywords[word] +=1
        
        overlap_score = 0
        for keyword in significant_base_keywords:
            if keyword in current_niche_keywords:
                # Score based on presence and frequency (simple sum for now)
                overlap_score += current_niche_keywords[keyword]
        
        if overlap_score > 0:
            # Normalize by the number of videos in the compared niche to avoid bias towards larger niches
            relatedness_scores[niche_name] = overlap_score / len(niche_videos)


    # Shared viewership (channels popular in both) - More complex, requires channel data across niches
    # This part would require a different data structure (e.g., mapping channels to niches they appear in)
    # For now, this aspect is omitted but noted for future enhancement.
    # Example pseudocode for shared channels:
    # base_niche_channels = {video.get('snippet', {}).get('channelId') for video in base_niche_videos}
    # for niche_name, niche_videos in all_available_videos_by_niche.items():
    #     if niche_name == base_niche_name: continue
    #     other_niche_channels = {video.get('snippet', {}).get('channelId') for video in niche_videos}
    #     shared_channel_count = len(base_niche_channels.intersection(other_niche_channels))
    #     if shared_channel_count > 0:
    #         relatedness_scores[niche_name] += shared_channel_count * X_WEIGHT_FACTOR # X_WEIGHT_FACTOR to be defined

    if not relatedness_scores:
        return []

    suggested_niches = [{"name": name, "relevance_score": score} for name, score in relatedness_scores.items()]
    suggested_niches.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return suggested_niches[:top_n]


def compare_niches(niches_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Compare trends across multiple niches or analyze a single niche.
    
    Args:
        niches_data: Dict where keys are niche names and values are lists of videos.
        
    Returns:
        Dictionary containing comparative analysis for each niche.
    """
    analysis_results = {}
    
    for niche_name, videos in niches_data.items():
        if not videos:
            analysis_results[niche_name] = {
                "error": "No video data provided for this niche.",
                "average_views": 0,
                "average_engagement_rate": 0,
                "top_videos": [],
                "top_channels_in_niche": [], # Requires channel data extraction from videos
                "trending_topics": []
            }
            continue

        total_views = sum(int(v.get('statistics', {}).get('viewCount', 0)) for v in videos)
        total_engagement_sum = 0 # Sum of (likes + comments)
        valid_videos_for_engagement = 0

        for v in videos:
            stats = v.get('statistics', {})
            views = int(stats.get('viewCount', 0))
            if views > 0:
                total_engagement_sum += int(stats.get('likeCount', 0)) + int(stats.get('commentCount', 0))
                valid_videos_for_engagement += 1
        
        average_views = total_views / len(videos) if videos else 0
        average_engagement_rate = (total_engagement_sum / total_views) if total_views > 0 else 0 # Overall engagement rate for the niche
        
        # Sort videos by score
        sorted_videos = sorted(videos, key=lambda v: calculate_video_score(v), reverse=True)
        
        # Extract unique channel IDs and their video counts/total views within this niche's video list
        channel_performance_in_niche = defaultdict(lambda: {"video_count": 0, "total_views": 0, "video_objects": []})
        for v in videos:
            channel_id = v.get('snippet', {}).get('channelId')
            if channel_id:
                channel_performance_in_niche[channel_id]["video_count"] += 1
                channel_performance_in_niche[channel_id]["total_views"] += int(v.get('statistics', {}).get('viewCount', 0))
                channel_performance_in_niche[channel_id]["video_objects"].append(v) # Store one video object for snippet access

        top_channels_in_niche_details = []
        # Create mock channel objects for scoring if full channel details aren't fetched separately
        for cid, data in channel_performance_in_niche.items():
            # To use calculate_channel_score, we need subscriber count, which isn't directly in video objects.
            # This part highlights dependency on having channel details.
            # For now, we can rank by total views or video count in the niche.
             # Or, if we assume first video's snippet might have channelTitle.
            channel_title = "Unknown Channel"
            if data["video_objects"]:
                channel_title = data["video_objects"][0].get("snippet", {}).get("channelTitle", "Unknown Channel")

            top_channels_in_niche_details.append({
                "id": cid,
                "title": channel_title, 
                "niche_video_count": data["video_count"],
                "niche_total_views": data["total_views"],
                # "score": calculate_channel_score(channel_mock_object, videos_for_this_channel_in_niche)
                # Actual channel score would require fetching channel details (subs) via youtube_api.py
            })
        
        # Sort channels by their total views within this niche's video set
        top_channels_in_niche_details.sort(key=lambda x: x["niche_total_views"], reverse=True)

        analysis_results[niche_name] = {
            "total_videos_in_selection": len(videos),
            "average_views": round(average_views),
            "average_engagement_rate": round(average_engagement_rate, 4),
            "top_videos": [
                {
                    "id": v.get("id"), 
                    "title": v.get("snippet", {}).get("title"), 
                    "views": int(v.get("statistics", {}).get("viewCount",0)),
                    "score": calculate_video_score(v)
                 } for v in sorted_videos[:5] # Top 5 videos
            ],
            "top_channels_in_niche": top_channels_in_niche_details[:5], # Top 5 channels based on performance within these videos
            "trending_topics": extract_topics_from_videos(videos, top_n=10) # Top 10 topics for this niche
        }
        
    return analysis_results

def analyze_video_trends(videos: List[Dict[str, Any]], top_n_videos: int = 10, top_n_topics: int = 10) -> Dict[str, Any]:
    """
    Analyze trends from a list of videos.
    
    Args:
        videos: List of video resources.
        top_n_videos: Number of top videos to return.
        top_n_topics: Number of top topics to return.
        
    Returns:
        Dictionary containing video trend analysis.
    """
    if not videos:
        return {
            "error": "No videos provided for analysis.",
            "average_views": 0,
            "average_engagement_rate": 0,
            "top_videos": [],
            "trending_topics": []
        }

    total_views = sum(int(v.get('statistics', {}).get('viewCount', 0)) for v in videos)
    total_engagement_sum = 0
    valid_videos_for_engagement = 0
    for v in videos:
        stats = v.get('statistics', {})
        views = int(stats.get('viewCount', 0))
        if views > 0:
            total_engagement_sum += int(stats.get('likeCount', 0)) + int(stats.get('commentCount', 0))
            valid_videos_for_engagement += 1
            
    average_views = total_views / len(videos) if videos else 0
    average_engagement_rate = (total_engagement_sum / total_views) if total_views > 0 else 0
    
    sorted_videos = sorted(videos, key=lambda v: calculate_video_score(v), reverse=True)
    
    return {
        "total_videos_analyzed": len(videos),
        "average_views": round(average_views),
        "average_engagement_rate": round(average_engagement_rate, 4),
        "top_videos": [
            {
                "id": v.get("id"), 
                "title": v.get("snippet", {}).get("title"), 
                "channel_title": v.get("snippet", {}).get("channelTitle"),
                "views": int(v.get("statistics", {}).get("viewCount",0)),
                "likes": int(v.get("statistics", {}).get("likeCount",0)),
                "comments": int(v.get("statistics", {}).get("commentCount",0)),
                "published_at": v.get("snippet", {}).get("publishedAt"),
                "score": calculate_video_score(v)
            } for v in sorted_videos[:top_n_videos]
        ],
        "trending_topics": extract_topics_from_videos(videos, top_n=top_n_topics)
    }

def analyze_channel_trends(
    channels_details: List[Dict[str, Any]], 
    videos_by_channel: Optional[Dict[str, List[Dict[str, Any]]]] = None, 
    top_n_channels: int = 10
) -> Dict[str, Any]:
    """
    Analyze trends from a list of channels. Requires full channel details for scoring.
    Optionally uses per-channel video lists to refine channel scores.
    
    Args:
        channels_details: List of channel resources (must include 'statistics' for subscriberCount).
        videos_by_channel: Optional. Dict mapping channelId to list of its videos. 
                           Used for avg. views and posting frequency in channel score.
        top_n_channels: Number of top channels to return.
        
    Returns:
        Dictionary containing channel trend analysis.
    """
    if not channels_details:
        return {
            "error": "No channel data provided for analysis.",
            "average_subscribers": 0,
            "top_channels": []
        }

    # Calculate scores for each channel
    scored_channels = []
    for ch_detail in channels_details:
        ch_id = ch_detail.get('id')
        channel_videos = videos_by_channel.get(ch_id, []) if videos_by_channel else []
        score = calculate_channel_score(ch_detail, channel_videos)
        scored_channels.append({**ch_detail, "score": score})

    sorted_channels = sorted(scored_channels, key=lambda c: c["score"], reverse=True)
    
    total_subscribers = sum(int(c.get('statistics', {}).get('subscriberCount', 0)) for c in channels_details if c.get('statistics'))
    average_subscribers = total_subscribers / len(channels_details) if channels_details else 0
    
    return {
        "total_channels_analyzed": len(channels_details),
        "average_subscribers": round(average_subscribers),
        "top_channels": [
            {
                "id": c.get("id"),
                "title": c.get("snippet", {}).get("title"),
                "subscribers": int(c.get("statistics", {}).get("subscriberCount", 0)),
                "video_count": int(c.get("statistics", {}).get("videoCount", 0)),
                "views": int(c.get("statistics", {}).get("viewCount", 0)), # Total views for the channel
                "published_at": c.get("snippet", {}).get("publishedAt"),
                "score": c.get("score")
            } for c in sorted_channels[:top_n_channels]
        ]
    }
