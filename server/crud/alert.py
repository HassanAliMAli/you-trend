from sqlalchemy.orm import Session
from typing import List, Optional

from server.models.alert import AlertSubscription as AlertModel
from server.schemas.alert import AlertSubscriptionCreate, AlertSubscriptionUpdate

def create_alert_subscription(db: Session, alert: AlertSubscriptionCreate, user_id: int) -> AlertModel:
    db_alert = AlertModel(
        **alert.dict(), 
        user_id=user_id
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_alert_subscription(db: Session, alert_id: int, user_id: int) -> Optional[AlertModel]:
    return db.query(AlertModel).filter(AlertModel.id == alert_id, AlertModel.user_id == user_id).first()

def get_alert_subscriptions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[AlertModel]:
    return db.query(AlertModel).filter(AlertModel.user_id == user_id).offset(skip).limit(limit).all()

def get_all_active_alert_subscriptions(db: Session, skip: int = 0, limit: int = 1000) -> List[AlertModel]: # For background worker
    return db.query(AlertModel).filter(AlertModel.is_active == True).offset(skip).limit(limit).all()

def update_alert_subscription(
    db: Session, 
    alert_id: int, 
    alert_update: AlertSubscriptionUpdate, 
    user_id: int
) -> Optional[AlertModel]:
    db_alert = get_alert_subscription(db, alert_id=alert_id, user_id=user_id)
    if db_alert:
        update_data = alert_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_alert, field, value)
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert
    return None

def delete_alert_subscription(db: Session, alert_id: int, user_id: int) -> Optional[AlertModel]:
    db_alert = get_alert_subscription(db, alert_id=alert_id, user_id=user_id)
    if db_alert:
        db.delete(db_alert)
        db.commit()
        return db_alert
    return None 