from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import FxRate


class RatesService:
    def __init__(self, db: Session):
        self.db = db

    def upsert_manual(self, from_currency: str, to_currency: str, rate: float, source: str = "manual") -> FxRate:
        row = FxRate(
            from_currency=from_currency.upper(),
            to_currency=to_currency.upper(),
            rate=rate,
            source=source,
            fetched_at=datetime.utcnow(),
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def fetch_mock_provider(self) -> int:
        payload = [
            ("SGD", "USD", 0.74),
            ("SGD", "EUR", 0.68),
            ("MYR", "USD", 0.21),
            ("MYR", "EUR", 0.19),
            ("SGD", "KZT", 350),
            ("MYR", "KZT", 100),
            ("SGD", "CNY", 5.3),
            ("MYR", "CNY", 1.5),
        ]
        for a, b, v in payload:
            self.upsert_manual(a, b, v, source="mock_fetch")
        return len(payload)
