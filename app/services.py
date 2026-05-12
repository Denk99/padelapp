from app.models import Notification, NotificationType
from datetime import datetime, timezone
from app.database import Session

def create_notification(
    session: Session,
    usuario_id: int,
    tipo: NotificationType,
    partido_id: int | None = None
):
    notification = Notification(
        usuario_id=usuario_id,
        partido_id=partido_id,
        tipo=tipo,
        creado_en=datetime.now(timezone.utc),
        leida=False
    )
    session.add(notification)