from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.models import AuditLog

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/profit")
def profit(_=Depends(require_role(UserRole.admin, UserRole.viewer))):
    return []


@router.get("/orders")
def orders(_=Depends(require_role(UserRole.admin, UserRole.viewer))):
    return []


@router.get("/problems")
def problems(_=Depends(require_role(UserRole.admin, UserRole.viewer))):
    return []


@router.get("/audit")
def audit(db: Session = Depends(get_db), _=Depends(require_role(UserRole.admin, UserRole.viewer))):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()
