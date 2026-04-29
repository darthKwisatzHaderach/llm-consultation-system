## Демонстрация

[demo/demo.mp4](demo/demo.mp4)

# LLM consultation (2 сервиса)

**Auth** — регистрация, логин, выдача JWT.  
**Bot** — Telegram, проверка JWT, очередь Celery, ответ через OpenRouter.

## Что нужно

- Python ≥ 3.11, [uv](https://github.com/astral-sh/uv), при варианте с Docker — установленный Docker / Docker Compose plugin
- Для бота без Docker: отдельно поднятый Redis и RabbitMQ; токен Telegram-бота через `@BotFather`, ключ [OpenRouter](https://openrouter.ai/)

## Откуда брать значения секретов

| Переменная | Назначение | Где взять |
| --- | --- | --- |
| **JWT_SECRET** | Общий симметричный ключ для подписи и проверки JWT в Auth и Bot; **должен совпадать** в обоих сервисах. | Любая достаточно длинная случайная строка (например `openssl rand -hex 32`), не передавать в открытых репозиториях и чатах. |
| **TELEGRAM_BOT_TOKEN** | Доступ HTTP API к нужному боту. | В Telegram: **`@BotFather`** → команда `/newbot` (или выбрать существующего бота) → в ответе будет токен вида `123456789:AAH…`. |
| **OPENROUTER_API_KEY** | Ключ к API OpenRouter для вызова LLM из Celery. | Сайт [openrouter.ai](https://openrouter.ai/) → раздел с API keys (ключ выдётся в личном кабинете). |

Для **локального запуска через `uv`** значения задаются в `auth_service/.env` и `bot_service/.env` (см. ниже). Для **Docker Compose** — в **корневом** файле `.env` рядом с `docker-compose.yml` (удобнее скопировать из `compose.env.example`).

## Установка (без Docker)

В каждом каталоге один раз:

```bash
cd auth_service && uv sync
cd ../bot_service && uv sync
```

Скопировать и поправить переменные:

- `auth_service/.env` — в первую очередь `JWT_SECRET`
- `bot_service/.env` — `TELEGRAM_BOT_TOKEN`, `OPENROUTER_API_KEY`, `JWT_SECRET` **такой же**, как в Auth; `REDIS_URL` и `RABBITMQ_URL` должны соответствовать реальным хостам Redis и RabbitMQ (в образце по умолчанию — `redis` и `rabbitmq`; при локальном запуске без Docker указать `localhost`)

## Docker Compose (Redis, RabbitMQ, Auth, Bot API, Celery, polling)

В репозитории есть `docker-compose.yml`: образы приложений собираются из `auth_service/` и `bot_service/`, имена сервисов внутри сети задают уже зафиксированные URL (**`AUTH_SERVICE_URL=http://auth:8000`**, **`REDIS_URL=redis://redis:6379/0`**, **`RABBITMQ_URL=…`** — менять через правку compose не требуется, если используются стандартные сервисы из файла).

1. В корне репозитория создать `.env`, например: `cp compose.env.example .env` и заполнить как минимум **JWT_SECRET**, **TELEGRAM_BOT_TOKEN**, **OPENROUTER_API_KEY** (значения — из таблицы выше). Файл `compose.env.example` задаёт только эти ключи под подстановку в compose; совпадает по смыслу с блоком `environment` в `docker-compose.yml`.
2. Запуск (сборка при первом заходе):  
   `docker compose up --build`  
   Фоново:  
   `docker compose up --build -d`
3. Остановка контейнеров: `docker compose down` (том SQLite для Auth сохраняется в именованном томе).

После старта: Swagger Auth — **http://127.0.0.1:8000/docs**; health Bot API — **http://127.0.0.1:8001/health**. Веб-интерфейс RabbitMQ (логин/пароль по умолчанию `guest` / `guest`): **http://127.0.0.1:15672**.

## Auth

```bash
cd auth_service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

При активном Compose тот же API обычно уже слушает порт **8000** на хосте.

Открыть Swagger: `http://127.0.0.1:8000/docs` — зарегистрировать пользователя, выполнить логин и скопировать `access_token`.

## Бот и воркеры

Нужны три процесса в отдельных терминалах (порядок не критичен, но Redis и RabbitMQ уже должны быть подняты):

1. **FastAPI** бота (метрика/health):

   ```bash
   cd bot_service
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
   ```

2. **Celery** (обработка LLM):

   ```bash
   cd bot_service
   uv run celery -A app.infra.celery_app:celery_app worker --loglevel=info
   ```

3. **Polling Telegram**:

   ```bash
   cd bot_service
   uv run python -m app.bot.dispatcher
   ```

При использовании **Docker Compose** эти три процесса соответствуют сервисам **`bot-api`**, **`celery-worker`**, **`telegram-bot`** (порты 8001 проброшен на хост; лог polling — вывод процесса `telegram-bot`, лог Celery — `celery-worker`).

Дальше в Telegram: команда `/token <JWT из Swagger>`, затем обычный текст — ответ приходит после того, как отработают очередь и OpenRouter.

## Тесты

Без реального Redis/RabbitMQ/OpenRouter внутри unit-тестов:

```bash
cd auth_service && uv run pytest
cd ../bot_service && uv run pytest
```

## Где что лежит

| Каталог       | Назначение                          |
| ------------- | ----------------------------------- |
| `auth_service/` | FastAPI + SQLite, JWT              |
| `bot_service/`  | aiogram, Celery, Redis, OpenRouter |

| Файл | Назначение |
| --- | --- |
| `compose.env.example` | Шаблон корневого `.env` для `docker compose` (только секреты под подстановку в `docker-compose.yml`) |
| `docker-compose.yml` | Redis, RabbitMQ, Auth, Bot API, Celery, telegram-bot и общая сеть |
