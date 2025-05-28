from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from server.utils import database, auth
from server.schemas import alert as alert_schema
from server.crud import alert as alert_crud
from server.models.user import User as UserModel

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    dependencies=[Depends(auth.get_current_active_user)] # All alert endpoints require active user
)

@router.post("", response_model=alert_schema.AlertSubscription, status_code=status.HTTP_201_CREATED)
def create_new_alert_subscription(
    alert: alert_schema.AlertSubscriptionCreate,
    db: Session = Depends(database.get_db),
    current_user: UserModel = Depends(auth.get_current_active_user)
):
    """Create a new alert subscription for the current user."""
    # TODO: Add validation for alert_type and criteria if needed
    # e.g., max number of active subscriptions per user
    return alert_crud.create_alert_subscription(db=db, alert=alert, user_id=current_user.id)

@router.get("", response_model=List[alert_schema.AlertSubscription])
def read_user_alert_subscriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: UserModel = Depends(auth.get_current_active_user)
):
    """Retrieve all alert subscriptions for the current user."""
    alerts = alert_crud.get_alert_subscriptions_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return alerts

@router.get("/{alert_id}", response_model=alert_schema.AlertSubscription)
def read_specific_alert_subscription(
    alert_id: int,
    db: Session = Depends(database.get_db),
    current_user: UserModel = Depends(auth.get_current_active_user)
):
    """Retrieve a specific alert subscription by ID for the current user."""
    db_alert = alert_crud.get_alert_subscription(db, alert_id=alert_id, user_id=current_user.id)
    if db_alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert subscription not found")
    return db_alert

@router.put("/{alert_id}", response_model=alert_schema.AlertSubscription)
def update_existing_alert_subscription(
    alert_id: int,
    alert: alert_schema.AlertSubscriptionUpdate,
    db: Session = Depends(database.get_db),
    current_user: UserModel = Depends(auth.get_current_active_user)
):
    """Update an existing alert subscription for the current user."""
    updated_alert = alert_crud.update_alert_subscription(db, alert_id=alert_id, alert_update=alert, user_id=current_user.id)
    if updated_alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert subscription not found or not owned by user")
    return updated_alert

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_alert_subscription(
    alert_id: int,
    db: Session = Depends(database.get_db),
    current_user: UserModel = Depends(auth.get_current_active_user)
):
    """Delete an existing alert subscription for the current user."""
    deleted_alert = alert_crud.delete_alert_subscription(db, alert_id=alert_id, user_id=current_user.id)
    if deleted_alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert subscription not found or not owned by user")
    return # No content for 204 