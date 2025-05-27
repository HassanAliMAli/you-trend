"""
Data Processing Module for YouTrend

This module analyzes YouTube data to identify trends, calculate metrics,
and generate insights for channels, videos, and topics.
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import pandas as pd
import numpy as np
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        engagement_rate = 0
        if view_count > 0:
            engagement_rate = (like_count + comment_count) / view_count
        
        # Calculate recency score (newer is better)
        published_at = snippet.get('publishedAt', '')
        if published_at:
            published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            days_since_published = (datetime.now().astimezone() - published_date).days
            recency_score = 1 / (1 + days_since_published) if days_since_published >= 0 else 0
        else:
            recency_score = 0
        
        # Calculate weighted score
        # Normalize view count (logarithmic scale)
        normalized_views = np.log1p(view_count) / 25  # Assuming max ~7B views (log(7B) ≈ 25)
        
        # Apply weights
        weighted_score = (
            0.4 * normalized_views +
            0.4 * min(engagement_rate, 1.0) +  # Corrected: Use engagement_rate (0-1 ratio), cap at 1.0
            0.2 * recency_score
        )
        
        return weighted_score
    
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
        videos: List of video resources for the channel (optional)
        
    Returns:
        Weighted score (higher is better)
    """
    try:
        # Extract metrics
        statistics = channel.get('statistics', {})
        
        subscriber_count = int(statistics.get('subscriberCount', 0))
        video_count = int(statistics.get('videoCount', 0))
        
        # Calculate average views
        avg_views = 0
        posting_frequency = 0
        
        if videos:
            # Calculate average views from provided videos
            view_counts = [int(v.get('statistics', {}).get('viewCount', 0)) for v in videos]
            if view_counts:
                avg_views = sum(view_counts) / len(view_counts)
            
            # Calculate posting frequency (videos per month)
            if len(videos) >= 2:
                publish_dates = [
                    datetime.fromisoformat(v.get('snippet', {}).get('publishedAt', '').replace('Z', '+00:00'))
                    for v in videos if v.get('snippet', {}).get('publishedAt')
                ]
                if len(publish_dates) >= 2:
                    publish_dates.sort()
                    days_span = (publish_dates[-1] - publish_dates[0]).days
                    if days_span > 0:
                        videos_per_day = len(publish_dates) / days_span
                        posting_frequency = videos_per_day * 30  # Convert to monthly
        
        # Normalize metrics
        normalized_subscribers = np.log1p(subscriber_count) / 20  # Assuming max ~100M subscribers
        normalized_views = np.log1p(avg_views) / 25  # Assuming max ~7B views
        normalized_frequency = min(posting_frequency / 30, 1)  # Cap at daily uploads (30/month)
        
        # Apply weights
        weighted_score = (
            0.3 * normalized_subscribers +
            0.4 * normalized_views +
            0.3 * normalized_frequency
        )
        
        return weighted_score
    
    except Exception as e:
        logging.error(f"Error calculating channel score for channel ID {channel.get('id', 'unknown')}: {e}", exc_info=True)
        return 0.0

def extract_topics_from_videos(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract trending topics and formats from video titles, tags, and descriptions
    
    Args:
        videos: List of video resources from YouTube API
        
    Returns:
        List of topic objects with name and count
    """
    if not videos:
        return []
    
    # Extract text from videos
    titles = [video.get('snippet', {}).get('title', '') for video in videos]
    descriptions = [video.get('snippet', {}).get('description', '') for video in videos]
    tags_lists = [video.get('snippet', {}).get('tags', []) for video in videos]
    
    # Flatten tags
    all_tags = [tag for tags in tags_lists if tags for tag in tags]
    
    # Process titles to extract formats/topics
    common_formats = [
        r'(\d+)\s*tips', r'how\s+to', r'tutorial', r'guide',
        r'review', r'top\s*(\d+)', r'best\s*(\d+)', r'worst\s*(\d+)',
        r'vs\.?', r'versus', r'comparison', r'react(?:ion)?s?',
        r'challenge', r'interview', r'explained', r'for beginners',
        r'gameplay', r'walkthrough', r'highlights?', r'montage',
        r'podcast', r'news', r'update', r'vlog'
    ]
    
    # Extract formats from titles
    format_matches = []
    for title in titles:
        title_lower = title.lower()
        for format_pattern in common_formats:
            matches = re.findall(format_pattern, title_lower)
            if matches:
                if isinstance(matches[0], tuple):
                    # Handle capturing groups
                    format_name = re.search(format_pattern, title_lower).group(0)
                else:
                    format_name = matches[0]
                format_matches.append(format_name)
    
    # Extract keywords from tags
    tag_counter = Counter(all_tags)
    
    # Combine formats and tags
    combined_counter = Counter(format_matches)
    for tag, count in tag_counter.most_common(50):  # Consider top 50 tags
        if len(tag.split()) <= 3 and len(tag) > 3:  # Only use tags with 1-3 words and longer than 3 chars
            combined_counter[tag] += count
    
    # Get the top topics
    top_topics = [
        {"name": topic, "count": count}
        for topic, count in combined_counter.most_common(20)
        if count >= 2  # Only include topics that appear at least twice
    ]
    
    return top_topics

def generate_video_ideas(topics: List[Dict[str, Any]], videos: List[Dict[str, Any]]) -> List[str]:
    """
    Generate actionable video ideas based on trending topics and top-performing videos
    
    Args:
        topics: List of topic objects with name and count
        videos: List of video resources from YouTube API
        
    Returns:
        List of video idea strings
    """
    if not topics or not videos:
        return []
    
    # Get top video formats
    format_topics = [
        topic for topic in topics
        if any(keyword in topic['name'].lower() for keyword in 
               ['how to', 'guide', 'tips', 'review', 'tutorial', 'top', 'best', 'challenge', 'reaction'])
    ]
    
    # Analyze video metrics
    view_counts = [int(video.get('statistics', {}).get('viewCount', 0)) for video in videos]
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
    
    # Find optimal video characteristics
    high_performing_idx = sorted(range(len(videos)), key=lambda i: view_counts[i], reverse=True)[:5]
    
    # Get durations of top videos
    durations = []
    for idx in high_performing_idx:
        try:
            video_item = videos[idx]
            duration = video_item.get('contentDetails', {}).get('duration', '')
            if duration:
                # Convert ISO 8601 duration to minutes
                minutes_match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
                if minutes_match:
                    hours = int(minutes_match.group(1) or 0)
                    mins = int(minutes_match.group(2) or 0)
                    secs = int(minutes_match.group(3) or 0)
                    total_minutes = hours * 60 + mins + secs / 60
                    durations.append(total_minutes)
        except Exception as e:
            video_id_for_error = video_item.get('id', 'unknown') if 'video_item' in locals() else 'unknown'
            logging.warning(f"Error parsing duration for video ID {video_id_for_error} (duration string: {duration}): {e}")
            # Continue, as one video failing duration parsing shouldn't stop all idea generation
    
    # Determine optimal duration range
    avg_duration = sum(durations) / len(durations) if durations else 10
    duration_desc = "short (3-5 minute)" if avg_duration < 10 else "medium (10-15 minute)" if avg_duration < 20 else "long-form (20+ minute)"
    
    # Generate ideas combining formats and topics
    ideas = []
    
    # Add format-based ideas
    for format_topic in format_topics[:3]:  # Use top 3 formats
        format_name = format_topic['name']
        if 'how to' in format_name.lower() or 'guide' in format_name.lower() or 'tutorial' in format_name.lower():
            ideas.append(f"Create a {duration_desc} 'How To' video focusing on specific techniques or solutions")
        elif 'review' in format_name.lower():
            ideas.append(f"Produce a {duration_desc} review video with clear pros and cons sections")
        elif 'tips' in format_name.lower():
            ideas.append(f"Make a {duration_desc} tips video highlighting {format_name}")
        elif 'top' in format_name.lower() or 'best' in format_name.lower():
            ideas.append(f"Create a {duration_desc} 'Top {5 if avg_duration < 10 else 10}' countdown video")
        elif 'challenge' in format_name.lower():
            ideas.append(f"Try a {duration_desc} challenge video that others can replicate")
    
    # Add general ideas based on overall analysis
    other_topics = [t for t in topics if t not in format_topics][:5]
    for topic in other_topics:
        ideas.append(f"Create a {duration_desc} video about '{topic['name']}' with an eye-catching thumbnail")
    
    # Add ideas based on engagement patterns
    if engagement_rates:
        if max(engagement_rates) > 0.1:  # High engagement
            ideas.append(f"Create a {duration_desc} video that asks viewers questions or prompts discussion in comments")
        else:
            ideas.append(f"Add clear calls-to-action throughout your {duration_desc} videos to increase engagement")
    
    # Deduplicate and limit ideas
    unique_ideas = list(set(ideas))
    return unique_ideas[:10]  # Return up to 10 unique ideas

def compare_niches(niches_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Compare multiple niches based on their videos and channels
    
    Args:
        niches_data: Dictionary mapping niche names to lists of video resources
        
    Returns:
        Dictionary with comparison metrics and insights
    """
    if not niches_data:
        return {}
    
    comparison_results = {
        'metrics': {},
        'rankings': {},
        'insights': []
    }
    
    # Calculate metrics for each niche
    for niche, videos in niches_data.items():
        if not videos:
            continue
        
        # Extract metrics
        view_counts = [int(video.get('statistics', {}).get('viewCount', 0)) for video in videos]
        like_counts = [int(video.get('statistics', {}).get('likeCount', 0)) for video in videos]
        comment_counts = [int(video.get('statistics', {}).get('commentCount', 0)) for video in videos]
        
        # Calculate engagement rates
        engagement_rates = []
        for i in range(len(videos)):
            if view_counts[i] > 0:
                engagement_rates.append((like_counts[i] + comment_counts[i]) / view_counts[i])
            else:
                engagement_rates.append(0)
        
        # Store metrics
        comparison_results['metrics'][niche] = {
            'video_count': len(videos),
            'avg_views': sum(view_counts) / len(view_counts) if view_counts else 0,
            'median_views': sorted(view_counts)[len(view_counts) // 2] if view_counts else 0,
            'max_views': max(view_counts) if view_counts else 0,
            'avg_engagement_rate': sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0,
            'topics': extract_topics_from_videos(videos)
        }
    
    # Rank niches by different metrics
    metrics_to_rank = ['avg_views', 'avg_engagement_rate', 'max_views']
    for metric in metrics_to_rank:
        ranked_niches = sorted(
            comparison_results['metrics'].keys(),
            key=lambda niche: comparison_results['metrics'][niche][metric],
            reverse=True
        )
        comparison_results['rankings'][metric] = ranked_niches
    
    # Generate insights
    insights = []
    
    # Insight about highest-viewed niche
    if 'avg_views' in comparison_results['rankings'] and comparison_results['rankings']['avg_views']:
        top_niche = comparison_results['rankings']['avg_views'][0]
        insights.append(f"The '{top_niche}' niche has the highest average views with {int(comparison_results['metrics'][top_niche]['avg_views']):,} views per video.")
    
    # Insight about engagement
    if 'avg_engagement_rate' in comparison_results['rankings'] and comparison_results['rankings']['avg_engagement_rate']:
        top_engaging_niche = comparison_results['rankings']['avg_engagement_rate'][0]
        insights.append(f"The '{top_engaging_niche}' niche has the highest audience engagement with an average engagement rate of {comparison_results['metrics'][top_engaging_niche]['avg_engagement_rate']:.1%}.")
    
    # Insight about topic overlap
    niche_topics = {
        niche: set([topic['name'] for topic in data['topics'][:5]]) 
        for niche, data in comparison_results['metrics'].items()
        if 'topics' in data and data['topics']
    }
    
    for niche1 in niche_topics:
        for niche2 in niche_topics:
            if niche1 != niche2:
                overlap = niche_topics[niche1].intersection(niche_topics[niche2])
                if len(overlap) >= 2:
                    insights.append(f"The '{niche1}' and '{niche2}' niches share similar topics: {', '.join(list(overlap))}.")
    
    comparison_results['insights'] = insights[:5]  # Limit to top 5 insights
    
    return comparison_results

def analyze_video_trends(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze trends in a collection of videos
    
    Args:
        videos: List of video resources from YouTube API
        
    Returns:
        Dictionary with trend analysis and insights
    """
    if not videos:
        return {}
    
    # Calculate scores and rank videos
    for video in videos:
        video['score'] = calculate_video_score(video)
    
    ranked_videos = sorted(videos, key=lambda v: v['score'], reverse=True)
    
    # Extract topics
    topics = extract_topics_from_videos(videos)
    
    # Generate video ideas
    ideas = generate_video_ideas(topics, ranked_videos[:20])  # Use top 20 videos for ideas
    
    # Analyze metadata trends
    title_lengths = [len(video.get('snippet', {}).get('title', '')) for video in videos]
    avg_title_length = sum(title_lengths) / len(title_lengths) if title_lengths else 0
    
    view_counts = [int(video.get('statistics', {}).get('viewCount', 0)) for video in videos]
    avg_views = sum(view_counts) / len(view_counts) if view_counts else 0
    
    # Extract thumbnail information (if available)
    thumbnail_types = defaultdict(int)
    for video in videos:
        thumbnails = video.get('snippet', {}).get('thumbnails', {})
        if 'maxres' in thumbnails:
            thumbnail_types['high_quality'] += 1
        elif 'high' in thumbnails:
            thumbnail_types['medium_quality'] += 1
        else:
            thumbnail_types['low_quality'] += 1
    
    # Return trend analysis
    return {
        'ranked_videos': ranked_videos,
        'topics': topics,
        'video_ideas': ideas,
        'metadata_insights': {
            'avg_title_length': avg_title_length,
            'avg_views': avg_views,
            'thumbnail_quality': dict(thumbnail_types)
        }
    }

def analyze_channel_trends(channels: List[Dict[str, Any]], videos_by_channel: Dict[str, List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Analyze trends among a collection of channels
    
    Args:
        channels: List of channel resources from YouTube API
        videos_by_channel: Dictionary mapping channel IDs to their videos
        
    Returns:
        Dictionary with channel trend analysis and insights
    """
    if not channels:
        return {}
    
    # Calculate scores and rank channels
    for channel in channels:
        channel_id = channel.get('id')
        channel_videos = videos_by_channel.get(channel_id, []) if videos_by_channel else []
        channel['score'] = calculate_channel_score(channel, channel_videos)
    
    ranked_channels = sorted(channels, key=lambda c: c['score'], reverse=True)
    
    # Analyze subscriber ranges
    subscriber_counts = [int(channel.get('statistics', {}).get('subscriberCount', 0)) for channel in channels]
    subscriber_ranges = {
        'small': sum(1 for count in subscriber_counts if count < 10_000),
        'medium': sum(1 for count in subscriber_counts if 10_000 <= count < 100_000),
        'large': sum(1 for count in subscriber_counts if 100_000 <= count < 1_000_000),
        'very_large': sum(1 for count in subscriber_counts if count >= 1_000_000)
    }
    
    # Analyze posting frequency (if videos are available)
    posting_frequency = {}
    if videos_by_channel:
        for channel_id, channel_videos in videos_by_channel.items():
            if len(channel_videos) >= 2:
                publish_dates = [
                    datetime.fromisoformat(v.get('snippet', {}).get('publishedAt', '').replace('Z', '+00:00'))
                    for v in channel_videos if v.get('snippet', {}).get('publishedAt')
                ]
                if len(publish_dates) >= 2:
                    publish_dates.sort()
                    days_span = (publish_dates[-1] - publish_dates[0]).days
                    if days_span > 0:
                        videos_per_day = len(publish_dates) / days_span
                        posting_frequency[channel_id] = videos_per_day * 30  # Convert to monthly
    
    # Return channel trend analysis
    return {
        'ranked_channels': ranked_channels,
        'subscriber_distribution': subscriber_ranges,
        'posting_frequency': posting_frequency,
        'top_performers': ranked_channels[:5]  # Top 5 channels
    }
