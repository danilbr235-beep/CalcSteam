from fastapi import APIRouter
from app.api.v1 import auth, dashboard, inventory, orders, pricing, rates, reports, settings

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(pricing.router)
api_router.include_router(inventory.router)
api_router.include_router(orders.router)
api_router.include_router(rates.router)
api_router.include_router(settings.router)
api_router.include_router(reports.router)
