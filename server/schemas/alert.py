from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AlertSubscriptionBase(BaseModel):
    alert_type: str # e.g., "keyword", "niche_trend"
    criteria: str # The keyword or niche identifier
    notification_method: Optional[str] = "email"
    is_active: bool = True

class AlertSubscriptionCreate(AlertSubscriptionBase):
    pass

class AlertSubscriptionUpdate(BaseModel):
    alert_type: Optional[str] = None
    criteria: Optional[str] = None
    notification_method: Optional[str] = None
    is_active: Optional[bool] = None

class AlertSubscriptionInDBBase(AlertSubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    last_checked_at: Optional[datetime] = None
    last_triggered_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AlertSubscription(AlertSubscriptionInDBBase):
    pass 