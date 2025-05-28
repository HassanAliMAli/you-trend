from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import os

from server.models.alert import AlertSubscription
from server.models.user import User
from server.crud.alert import update_alert_subscription # To update last_checked_at
from server.schemas.alert import AlertSubscriptionUpdate # For type hint
from server.utils import youtube_api, data_processor
from server.crud import alert as alert_crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a simple threshold for what constitutes a "new" trend for an alert
# E.g., video published within the last X hours, or significant view count jump
# This can be made more sophisticated or configurable per alert later.
NEW_TREND_WINDOW_HOURS = 24 

def check_single_alert_subscription(
    db: Session, 
    alert_sub: AlertSubscription, 
    user_api_key: str # User's specific API key or a system key
) -> bool:
    """
    Checks a single alert subscription for new trends.
    Returns True if a notification should be triggered, False otherwise.
    Updates the alert_sub's last_checked_at time.
    """
    notification_needed = False
    now = datetime.utcnow()
    
    try:
        logger.info(f"Checking alert ID {alert_sub.id} for user {alert_sub.user_id}: Type '{alert_sub.alert_type}', Criteria '{alert_sub.criteria}'")

        # Determine the effective 'since' time for checking new items
        # Use last_triggered_at if available and recent, otherwise last_checked_at, or a default window
        since_time = alert_sub.last_triggered_at
        if not since_time or (now - since_time) > timedelta(days=7): # If not triggered in a while, broaden scope a bit
            since_time = alert_sub.last_checked_at
        if not since_time: # If never checked or triggered, look back defined window
            since_time = now - timedelta(hours=NEW_TREND_WINDOW_HOURS * 2) # Look a bit further back first time
        else: # If recently checked/triggered, only look for things newer than that.
             since_time = max(since_time, now - timedelta(hours=NEW_TREND_WINDOW_HOURS * 2)) # Ensure we don't miss things if worker runs infrequently
        
        # Convert since_time to ISO format string for YouTube API
        published_after_filter = since_time.isoformat("T") + "Z"

        if alert_sub.alert_type == "keyword":
            # Search for new videos with this keyword published after since_time
            videos = youtube_api.search_videos(
                query=alert_sub.criteria,
                order="date", # Get newest first
                max_results=5, # Check a few recent ones
                api_key=user_api_key,
                published_after=published_after_filter
            )
            if videos:
                logger.info(f"Alert ID {alert_sub.id}: Found {len(videos)} new videos for keyword '{alert_sub.criteria}'.")
                # Simple trigger: if any new video is found.
                # More complex logic: check view counts, relevance, etc.
                notification_needed = True
        
        elif alert_sub.alert_type == "niche_trend":
            # For a niche, we might look for top trending videos in that niche (category) or by searching
            # This is more complex as "niche trend" isn't a direct API call.
            # Let's assume 'criteria' is a search term for the niche.
            videos = youtube_api.search_videos(
                query=alert_sub.criteria,
                order="viewCount", # Look for high view count, recent videos
                max_results=5,
                api_key=user_api_key,
                published_after=published_after_filter 
            )
            # Analyze if these represent a significant new trend (e.g., high velocity)
            # For simplicity, if highly viewed recent videos are found, trigger.
            if videos:
                analyzed_niche = data_processor.analyze_video_trends(videos, top_n_videos=1, top_n_topics=1)
                if analyzed_niche["top_videos"] and analyzed_niche["average_views"] > 10000: # Arbitrary threshold
                    logger.info(f"Alert ID {alert_sub.id}: Found new trend activity for niche '{alert_sub.criteria}'.")
                    notification_needed = True

        # Add more alert_type handlers (e.g., "channel_update") if needed

        if notification_needed:
            alert_sub.last_triggered_at = now

    except youtube_api.YouTubeApiError as yte:
        logger.error(f"YouTube API error checking alert ID {alert_sub.id}: {yte.detail}")
        # Potentially mark alert as having issues or notify user of API key problem
    except Exception as e:
        logger.error(f"Error checking alert ID {alert_sub.id}: {e}", exc_info=True)
    finally:
        # Always update last_checked_at
        alert_sub.last_checked_at = now
        db.add(alert_sub)
        db.commit()
        # db.refresh(alert_sub) # Not strictly necessary if only updating timestamps

    return notification_needed 

def process_all_alerts(db: Session):
    """
    Processes all active alert subscriptions.
    This function would be called periodically by a scheduler.
    """
    logger.info("Starting background process for all active alerts...")
    active_subscriptions = alert_crud.get_all_active_alert_subscriptions(db, limit=10000) # Get a large batch

    if not active_subscriptions:
        logger.info("No active alert subscriptions to process.")
        return

    processed_count = 0
    triggered_count = 0

    for alert_sub in active_subscriptions:
        user = alert_sub.owner # Access the user through the relationship
        if not user:
            logger.warning(f"Alert subscription ID {alert_sub.id} has no owner. Skipping.")
            continue
        
        # Determine API key to use
        api_key_to_use = user.youtube_api_key
        if not api_key_to_use:
            # Fallback to system API key if user hasn't set one
            api_key_to_use = os.getenv("YOUTUBE_API_KEY") 
        
        if not api_key_to_use:
            logger.warning(f"No API key available for user {user.id} (alert {alert_sub.id}). Skipping alert check.")
            # Optionally update alert_sub.last_checked_at here even if skipped due to no key
            alert_sub.last_checked_at = datetime.utcnow()
            db.add(alert_sub)
            db.commit()
            continue

        try:
            if check_single_alert_subscription(db=db, alert_sub=alert_sub, user_api_key=api_key_to_use):
                triggered_count += 1
                # Actual notification logic would go here (e.g., send email, create in-app notification)
                logger.info(f"Notification TRIGGERED for alert ID {alert_sub.id} (User: {user.id}, Type: {alert_sub.alert_type}, Criteria: '{alert_sub.criteria}')")
                # Example: Create a simple notification record in another table or log to a specific file
            processed_count += 1
        except Exception as e:
            logger.error(f"Unhandled error processing alert ID {alert_sub.id} for user {user.id}: {e}", exc_info=True)
            # Ensure last_checked_at is updated even if there was an unhandled error in the check itself
            alert_sub.last_checked_at = datetime.utcnow()
            db.add(alert_sub)
            db.commit()
            
    logger.info(f"Finished processing alerts. Checked: {processed_count}, Triggered: {triggered_count}") 