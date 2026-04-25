from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select, Session
from sqlalchemy import desc, update, false
from app.models import Notification, NotificationCreate, NotificationRead, NotificationType
from app.dependencies import get_session
from app.security import CurrentPlayer
from datetime import datetime, timezone

router = APIRouter()

# GET Methods
    # GET Unread notifications
@router.get("/notifications/unread/", response_model=list[NotificationRead])
def get_unread_notifications(current_player: CurrentPlayer, session: Session = Depends(get_session)):
    notifications = session.exec(
        select(Notification)
        .where(Notification.usuario_id == current_player.id)
        .where(Notification.leida == False)
        .order_by(desc(getattr(Notification, "creado_en")))
    ).all()
    if not notifications:
        raise HTTPException(status_code=404, detail="No unread notifications")
    return notifications

    # GET Notification by ID 
@router.get("/notifications/{notification_id}", response_model=NotificationRead)
def get_notification_by_id(notification_id: int, current_player: CurrentPlayer, session: Session = Depends(get_session)):
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

    # GET All notifications of specific player
@router.get("/notifications/", response_model=list[NotificationRead])
def get_all_notifications(current_player: CurrentPlayer, session: Session = Depends(get_session)):
    notifications = session.exec(
        select(Notification)
        .where(Notification.usuario_id == current_player.id)
        .order_by(desc(getattr(Notification, "creado_en")))
    ).all()
    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications")
    return notifications

# POST Methods
    # POST Notification
@router.post("/notifications/", response_model=NotificationRead)
def post_notification(
    notification: NotificationCreate,
    session: Session = Depends(get_session)
):
    if notification.tipo not in NotificationType.__members__.values():
        raise HTTPException(status_code=400, detail="Invalid notification type")
    
    db_notification = Notification.from_orm(notification)
    db_notification.creado_en = datetime.now(timezone.utc)
    db_notification.leida = False
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)
    return db_notification


# PATCH Methods
    # UPDATE Notification from unread to read
@router.patch("/notifications/read", status_code=200)
def mark_notifications_as_read(current_player: CurrentPlayer, session: Session = Depends(get_session)):
    if current_player.id is None:
        raise HTTPException(status_code=401, detail="Invalid user")
    notifications_to_update = (
        update(Notification)
        .where(Notification.usuario_id == current_player) # type: ignore
        .values(leida=True)
    )
    result = session.exec(notifications_to_update)
    session.commit()
    updated = result.rowcount if result.rowcount is not None else 0
    return {"message": "OK", "updated": updated}


# DELETE Methods
    # DELETE Notification by ID
@router.delete("/notifications/{notification_id}", status_code=200)
def delete_notification_by_id(notification_id: int, current_player: CurrentPlayer, session: Session = Depends(get_session)):
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    session.delete(notification)
    session.commit()
    return {"message": "Deleted", "id": notification_id}