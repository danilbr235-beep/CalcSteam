from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.models import Order, User
from app.schemas.orders import CreateOrderRequest, FulfillResponse, ReserveOrderRequest
from app.services.order_service import OrderService
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
def list_orders(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    return db.query(Order).all()


@router.post("")
def create_order(
    payload: CreateOrderRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator)),
):
    return OrderService(db).create_order(
        external_ref=payload.external_ref,
        sell_nominal_id=payload.sell_nominal_id,
        expected_revenue_rub=payload.expected_revenue_rub,
    )


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.admin, UserRole.operator, UserRole.viewer)),
):
    return db.query(Order).filter(Order.id == order_id).first()


@router.post("/{order_id}/reserve")
def reserve(
    order_id: int,
    payload: ReserveOrderRequest,
    idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.admin, UserRole.operator)),
):
    try:
        ReservationService(db).reserve_codes(
            order_id,
            payload.code_ids,
            ttl_minutes=payload.ttl_minutes,
            idempotency_key=idempotency_key,
            user_id=user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"ok": True}


@router.post("/{order_id}/fulfill", response_model=FulfillResponse)
def fulfill(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        codes = OrderService(db).fulfill(order_id, user)
    except ValueError as exc:
        code = 403 if str(exc) == "Forbidden" else 409
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    return FulfillResponse(order_id=order_id, codes=codes, status="fulfilled")


@router.post("/{order_id}/problem")
def mark_problem(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.admin, UserRole.operator)),
):
    OrderService(db).mark_problem(order_id, user.id)
    return {"ok": True}


@router.post("/{order_id}/complete")
def complete(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.admin, UserRole.operator)),
):
    OrderService(db).complete(order_id, user.id)
    return {"ok": True}
