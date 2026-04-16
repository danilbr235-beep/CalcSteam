from apscheduler.schedulers.background import BackgroundScheduler
from app.db.session import SessionLocal
from app.services.pricing_service import PricingService
from app.services.rates_service import RatesService
from app.services.reservation_service import ReservationService


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")

    def clear_expired_job():
        db = SessionLocal()
        try:
            ReservationService(db).clear_expired_with_lock()
        finally:
            db.close()

    def fetch_rates_job():
        db = SessionLocal()
        try:
            RatesService(db).fetch_mock_provider()
        finally:
            db.close()

    def recalc_pricing_job():
        db = SessionLocal()
        try:
            PricingService(db).recalculate_all(default_revenue_rub=1000)
        finally:
            db.close()

    scheduler.add_job(clear_expired_job, "interval", minutes=2, id="clear_expired")
    scheduler.add_job(fetch_rates_job, "interval", hours=1, id="fetch_rates")
    scheduler.add_job(recalc_pricing_job, "interval", hours=1, id="recalc_pricing")
    scheduler.start()
    return scheduler
