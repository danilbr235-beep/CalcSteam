from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.models import CodeItem, PurchaseBatch, User
from app.schemas.inventory import CodeCreateRequest, CodeRead, CodeStatusPatch
from app.services.audit_service import log_action
from app.utils.crypto import decrypt_code, encrypt_code, mask_code

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/batches")
def batches(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    return db.query(PurchaseBatch).all()


@router.post("/import")
def import_codes(
    payload: list[CodeCreateRequest],
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.admin, UserRole.operator)),
):
    created = 0
    for row in payload:
        db.add(
            CodeItem(
                batch_id=row.batch_id,
                supplier_code_type_id=row.supplier_code_type_id,
                encrypted_code=encrypt_code(row.raw_code),
                masked_code=mask_code(row.raw_code),
                purchase_cost_rub=row.purchase_cost_rub,
            )
        )
        created += 1
    db.commit()
    log_action(db, user.id, "inventory.import", "code_item", "batch", {"count": created})
    return {"created": created}


@router.post("/codes", response_model=CodeRead)
def create_code(
    payload: CodeCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.admin, UserRole.operator)),
):
    row = CodeItem(
        batch_id=payload.batch_id,
        supplier_code_type_id=payload.supplier_code_type_id,
        encrypted_code=encrypt_code(payload.raw_code),
        masked_code=mask_code(payload.raw_code),
        purchase_cost_rub=payload.purchase_cost_rub,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    log_action(db, user.id, "inventory.create_code", "code_item", str(row.id), {"masked": row.masked_code})
    return row


@router.get("/codes", response_model=list[CodeRead])
def list_codes(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    return db.query(CodeItem).order_by(CodeItem.id.desc()).limit(300).all()


@router.get("/codes/{code_id}/reveal")
def reveal_code(
    code_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role not in [UserRole.admin, UserRole.operator]:
        raise HTTPException(status_code=403, detail="Forbidden")
    code = db.query(CodeItem).filter(CodeItem.id == code_id).first()
    if not code:
        raise HTTPException(status_code=404, detail="Not found")
    plain = decrypt_code(code.encrypted_code)
    log_action(db, user.id, "inventory.reveal", "code_item", str(code_id), {})
    return {"code": plain}


@router.patch("/codes/{code_id}/status")
def patch_status(
    code_id: int,
    payload: CodeStatusPatch,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.admin, UserRole.operator)),
):
    row = db.query(CodeItem).filter(CodeItem.id == code_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    row.status = payload.status
    db.commit()
    log_action(db, user.id, "inventory.status", "code_item", str(code_id), {"status": payload.status.value})
    return {"ok": True}


@router.get("/stock-summary")
def stock_summary(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    return {
        "new": db.query(CodeItem).filter(CodeItem.status == "new").count(),
        "reserved": db.query(CodeItem).filter(CodeItem.status == "reserved").count(),
        "sent": db.query(CodeItem).filter(CodeItem.status == "sent").count(),
    }
