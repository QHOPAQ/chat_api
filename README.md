# Chat API

Тестовое задание: REST API для чатов и сообщений.

Backend-приложение на **FastAPI** с использованием **PostgreSQL**, **SQLAlchemy**, **Alembic**.  
Приложение полностью разворачивается и запускается через **Docker Compose**.

---

## Функциональность

### Модели

**Chat**
- `id: int`
- `title: str` — не пустой, длина 1–200, trim пробелов
- `created_at: datetime`

**Message**
- `id: int`
- `chat_id: int` — внешний ключ на Chat
- `text: str` — не пустой, длина 1–5000
- `created_at: datetime`

Связь: **Chat 1 — N Message**  
При удалении чата все связанные сообщения удаляются каскадно.

---

## API

### POST `/chats/`
Создать чат

```json
{
  "title": "My chat"
}
```

---

### POST `/chats/{id}/messages/`
Отправить сообщение в чат

```json
{
  "text": "Hello"
}
```

Если чат не существует — `404 Not Found`.

---

### GET `/chats/{id}`
Получить чат и последние сообщения

Query parameters:
- `limit` — количество сообщений (по умолчанию 20, максимум 100)

Сообщения возвращаются отсортированными по `created_at`
(от старых к новым среди последних `limit` сообщений).

---

### DELETE `/chats/{id}`
Удалить чат вместе со всеми сообщениями

Response:
- `204 No Content`

---

## Валидация и ограничения

- Нельзя отправить сообщение в несуществующий чат
- `title`: длина 1–200, не пустой, trim пробелов
- `text`: длина 1–5000, не пустой
- `limit` — максимум 100
- Каскадное удаление сообщений реализовано на уровне БД и ORM

---

## Технологии

- Python 3.12
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Docker / Docker Compose
- pytest

---

## Архитектура проекта

```
chat_api/
├── src/
│   ├── api/routes/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   └── main.py
├── migrations/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
└── README.md
```

---

## Запуск проекта

### Требования
- Docker
- Docker Compose

### Запуск
```bash
docker compose up --build
```

После запуска:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

Миграции базы данных применяются автоматически при старте контейнера.

---

## Тесты

Запуск тестов внутри Docker:

```bash
docker compose exec app pytest
```

---

