import hashlib
from sqlalchemy.orm import Session
from app.models.enums import CodeStatus, OrderStatus, UserRole
from app.models.models import CodeItem, Order, OrderFulfillment, User
from app.services.audit_service import log_action
from app.utils.crypto import decrypt_code


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, external_ref: str, sell_nominal_id: int, expected_revenue_rub: float) -> Order:
        row = Order(
            external_ref=external_ref,
            sell_nominal_id=sell_nominal_id,
            expected_revenue_rub=expected_revenue_rub,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def fulfill(self, order_id: int, operator: User) -> list[str]:
        if operator.role not in [UserRole.admin, UserRole.operator]:
            raise ValueError("Forbidden")
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        codes = (
            self.db.query(CodeItem)
            .filter(
                CodeItem.reserved_order_id == order_id,
                CodeItem.status == CodeStatus.reserved,
            )
            .all()
        )
        if not codes:
            raise ValueError("No reserved codes")
        revealed = []
        for code in codes:
            plain = decrypt_code(code.encrypted_code)
            revealed.append(plain)
            code.status = CodeStatus.sent
            self.db.add(
                OrderFulfillment(
                    order_id=order_id,
                    operator_user_id=operator.id,
                    code_item_id=code.id,
                    revealed_code_hash=hashlib.sha256(plain.encode()).hexdigest(),
                )
            )
        order.status = OrderStatus.fulfilled
        self.db.commit()
        log_action(
            self.db,
            operator.id,
            "order.fulfill",
            "order",
            str(order_id),
            {"codes_count": len(codes)},
        )
        return revealed

    def mark_problem(self, order_id: int, user_id: int | None = None) -> None:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        order.status = OrderStatus.problem
        self.db.commit()
        log_action(self.db, user_id, "order.problem", "order", str(order_id), {})

    def complete(self, order_id: int, user_id: int | None = None) -> None:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        order.status = OrderStatus.completed
        self.db.commit()
        log_action(self.db, user_id, "order.complete", "order", str(order_id), {})
