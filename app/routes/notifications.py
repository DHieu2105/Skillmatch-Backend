from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.notification import Notification
from ..schemas.notification import NotificationResponse


router = APIRouter(prefix="/notifications")


@router.get("", response_model=list[NotificationResponse])
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.upper() != "STUDENT":
        raise HTTPException(status_code=403, detail="Student role required")

    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.user_id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return notifications


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role.upper() != "STUDENT":
        raise HTTPException(status_code=403, detail="Student role required")

    notification = db.query(Notification).filter(
        Notification.notification_id == notification_id,
        Notification.user_id == current_user.user_id,
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return notification
