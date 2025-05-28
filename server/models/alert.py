from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class AlertSubscription(Base):
    __tablename__ = "alert_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Alert criteria
    alert_type = Column(String, index=True, nullable=False) # e.g., "keyword", "niche", "channel_update"
    criteria = Column(String, nullable=False) # The actual keyword, niche name, channel ID, etc.
    
    # Notification preferences (simplified for now)
    notification_method = Column(String, default="email") # Could be "email", "in_app", etc.
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_checked_at = Column(DateTime(timezone=True), nullable=True) # When this alert was last processed
    last_triggered_at = Column(DateTime(timezone=True), nullable=True) # When this alert last found a match

    owner = relationship("User") # Relationship to the User model 