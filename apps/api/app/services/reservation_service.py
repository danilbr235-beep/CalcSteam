from datetime import datetime, timedelta
from typing import Any
import redis
from redis.exceptions import RedisError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.enums import CodeStatus, OrderStatus
from app.models.models import CodeItem, Order
from app.services.audit_service import log_action


class InMemoryLockStore:
    def __init__(self):
        self._store: dict[str, tuple[str, datetime | None]] = {}

    def _alive(self, key: str) -> bool:
        val = self._store.get(key)
        if not val:
            return False
        _, exp = val
        if exp and exp < datetime.utcnow():
            self._store.pop(key, None)
            return False
        return True

    def set(self, key: str, value: str, ex: int | None = None, nx: bool = False):
        if nx and self._alive(key):
            return False
        exp = datetime.utcnow() + timedelta(seconds=ex) if ex else None
        self._store[key] = (value, exp)
        return True

    def delete(self, key: str):
        self._store.pop(key, None)


def _build_lock_store() -> Any:
    try:
        client = redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        return client
    except Exception:  # noqa: BLE001
        return InMemoryLockStore()


rds = _build_lock_store()


class ReservationService:
    def __init__(self, db: Session):
        self.db = db

    def reserve_codes(
        self,
        order_id: int,
        code_ids: list[int],
        ttl_minutes: int | None = None,
        idempotency_key: str | None = None,
        user_id: int | None = None,
    ) -> None:
        ttl = ttl_minutes or settings.reservation_ttl_minutes
        anti_double_key = f"lock:order:{order_id}:{idempotency_key or 'default'}"
        if not rds.set(anti_double_key, "1", ex=15, nx=True):
            raise ValueError("Double click lock")

        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        rows = self.db.query(CodeItem).filter(CodeItem.id.in_(code_ids)).with_for_update().all()
        if len(rows) != len(code_ids):
            raise ValueError("Some codes not found")
        for code in rows:
            if code.status != CodeStatus.new:
                raise ValueError(f"Code {code.id} already used")
            redis_key = f"reserve:code:{code.id}"
            if not rds.set(redis_key, str(order_id), ex=ttl * 60, nx=True):
                raise ValueError(f"Code {code.id} already reserved")
            code.status = CodeStatus.reserved
            code.reserved_order_id = order_id
            code.reserved_until = datetime.utcnow() + timedelta(minutes=ttl)
        order.status = OrderStatus.reserved
        self.db.commit()
        log_action(self.db, user_id, "order.reserve", "order", str(order_id), {"code_ids": code_ids, "ttl": ttl})

    def clear_expired(self) -> int:
        now = datetime.utcnow()
        rows = (
            self.db.query(CodeItem)
            .filter(CodeItem.status == CodeStatus.reserved, CodeItem.reserved_until < now)
            .all()
        )
        for code in rows:
            rds.delete(f"reserve:code:{code.id}")
            code.status = CodeStatus.new
            code.reserved_order_id = None
            code.reserved_until = None
        self.db.commit()
        return len(rows)

    def clear_expired_with_lock(self) -> int:
        lock_key = "lock:job:clear_expired"
        if not rds.set(lock_key, "1", ex=50, nx=True):
            return 0
        try:
            return self.clear_expired()
        finally:
            rds.delete(lock_key)
