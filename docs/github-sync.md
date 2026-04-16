# Как синхронизировать проект с GitHub

## 1) Создай репозиторий на GitHub

Создай пустой репозиторий (без README/license/gitignore) в своем аккаунте.

## 2) Подключи remote

В корне проекта:

```bash
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
```

Проверка:

```bash
git remote -v
```

## 3) Отправь текущую ветку

```bash
git push -u origin <YOUR_BRANCH>
```

Если хочешь отправить в `main`:

```bash
git branch -M main
git push -u origin main
```

## 4) Вариант с SSH

Если используешь SSH-ключи:

```bash
git remote set-url origin git@github.com:<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin <YOUR_BRANCH>
```

## 5) Personal Access Token (HTTPS)

Если GitHub просит пароль, используй PAT вместо пароля.

1. GitHub → Settings → Developer settings → Personal access tokens.
2. Создай token с правами `repo`.
3. Используй token в login prompt git.

## 6) Что происходит автоматически после push

В репозитории добавлен GitHub Actions workflow (`.github/workflows/ci.yml`), который запускает:
- API тесты (`pytest -q`)
- Web build (`npm run build`)

Это позволяет проверять качество изменений на каждом push/PR.
