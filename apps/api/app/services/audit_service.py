from sqlalchemy.orm import Session
from app.models.models import AuditLog


def log_action(db: Session, user_id: int | None, action: str, entity_type: str, entity_id: str, metadata: dict | None = None) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata or {},
        )
    )
    db.commit()
