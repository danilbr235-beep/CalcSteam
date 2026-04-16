# CalcSteam Monorepo

Внутренняя admin-панель для расчета цен, подбора комбинаций Steam-кодов (SGD/MYR), резервирования и выдачи заказов.

## Архитектура

- `apps/api` — FastAPI + SQLAlchemy + Alembic + Redis
- `apps/web` — Next.js 14 + TypeScript + Tailwind + React Query + Zustand
- `packages/shared` — общие типы/константы
- `infra` — docker-compose и nginx
- `docs` — техническая документация

## Локальный запуск

```bash
cp .env.example .env
docker compose up --build
```

- API: `http://localhost:8000/docs`
- Web: `http://localhost:3000`

## Backend setup (без Docker)

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e .
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

## Миграции

```bash
cd apps/api
alembic upgrade head
```

## Seed

```bash
cd apps/api
python -m app.db.seed
```

## Переменные окружения

См. `.env.example`.

## Роли

- `admin`: полный доступ, пользователи, настройки, закупки
- `operator`: работа с заказами, резерв/выдача кодов
- `viewer`: read-only, без просмотра полных кодов

## Pricing engine

Использует настраиваемые параметры из `pricing_configs` и формулы из ТЗ.

Алгоритм:
1. Берет витринный номинал
2. Считает доставленное значение комбинации по FX
3. Применяет формулы стоимости/маржи
4. Фильтрует по tolerance
5. Ранжирует: max profit → min codes → min deviation
6. Ставит `stale_rate` если курсы устарели

## Reservation & fulfillment flow (ЭТАП 3)

- Резерв кода обязателен перед выдачей.
- Reserve endpoint поддерживает anti-double-click через `X-Idempotency-Key`.
- Резервы хранятся с TTL, просроченные снимаются фоновым джобом.
- `viewer` не может раскрывать код и не может fulfill заказ.
- Полный reveal кода доступен только `admin/operator` и аудитируется.

## Scheduler jobs

- hourly `fetch_rates`
- hourly `recalc_pricing`
- every 2 min `clear_expired` (с distributed lock)

## GitHub sync

Проект **не пушится автоматически** в ваш GitHub, пока не настроен `origin`.

Подробная инструкция: `docs/github-sync.md`.

Быстрый старт:

```bash
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin <YOUR_BRANCH>
```

## CI

Добавлен GitHub Actions workflow `.github/workflows/ci.yml`:
- `apps/api`: `pytest -q`
- `apps/web`: `npm run build`

## Тесты

```bash
cd apps/api
pytest -q
```
