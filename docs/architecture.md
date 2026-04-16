# Архитектура CalcSteam

Система разделена на API и Web с общей PostgreSQL и Redis.

- FastAPI сервисный слой: pricing, reservation, order fulfillment.
- Pricing snapshots рассчитываются по расписанию и вручную.
- Redis хранит lock-ключи и TTL резервов.
