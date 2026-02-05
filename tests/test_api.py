import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy import event, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.models.message import Message
from src.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Ensure SQLite enforces foreign keys so we can actually test cascade deletes.
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):  # noqa: ARG001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c, TestingSessionLocal

    app.dependency_overrides.clear()


def test_create_chat_trims_title(client):
    c, _ = client
    r = c.post("/chats/", json={"title": "  My Chat  "})
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "My Chat"
    assert "id" in data


def test_validation_title_trim_and_length(client):
    c, _ = client
    r = c.post("/chats/", json={"title": "   "})
    assert r.status_code == 422

    r = c.post("/chats/", json={"title": "a" * 201})
    assert r.status_code == 422


def test_send_message_404_if_chat_not_found(client):
    c, _ = client
    r = c.post("/chats/999/messages/", json={"text": "Hello"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Chat not found"


def test_messages_limit_and_order(client):
    c, _ = client
    r = c.post("/chats/", json={"title": "Chat"})
    chat_id = r.json()["id"]

    c.post(f"/chats/{chat_id}/messages/", json={"text": "first"})
    c.post(f"/chats/{chat_id}/messages/", json={"text": "second"})
    c.post(f"/chats/{chat_id}/messages/", json={"text": "third"})

    r = c.get(f"/chats/{chat_id}?limit=2")
    assert r.status_code == 200
    body = r.json()
    msgs = body["messages"]
    assert len(msgs) == 2
    # last 2 messages returned, sorted by created_at ascending
    assert msgs[0]["text"] == "second"
    assert msgs[1]["text"] == "third"

    r = c.get(f"/chats/{chat_id}?limit=999")
    assert r.status_code == 422


def test_cascade_delete_messages(client):
    c, SessionLocal = client
    r = c.post("/chats/", json={"title": "Chat"})
    chat_id = r.json()["id"]

    c.post(f"/chats/{chat_id}/messages/", json={"text": "hello"})
    c.post(f"/chats/{chat_id}/messages/", json={"text": "world"})

    # Ensure messages exist
    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(Message).where(Message.chat_id == chat_id))
        assert count == 2

    r = c.delete(f"/chats/{chat_id}")
    assert r.status_code == 204

    r = c.get(f"/chats/{chat_id}")
    assert r.status_code == 404

    # Cascade should remove all messages for this chat.
    with SessionLocal() as db:
        remaining = db.scalars(select(Message).where(Message.chat_id == chat_id)).all()
        assert remaining == []

def test_health(client):
    c, _ = client
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_validation_text_trim_and_length(client):
    c, _ = client
    r = c.post("/chats/", json={"title": "Chat"})
    chat_id = r.json()["id"]

    r = c.post(f"/chats/{chat_id}/messages/", json={"text": "   "})
    assert r.status_code == 422

    r = c.post(f"/chats/{chat_id}/messages/", json={"text": "a" * 5001})
    assert r.status_code == 422
