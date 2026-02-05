import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from src.models.chat import Chat
from src.models.message import Message

logger = logging.getLogger("chat_service")

class NotFoundError(Exception):
    pass

def create_chat(db: Session, title: str) -> Chat:
    chat = Chat(title=title)
    db.add(chat)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("create_chat_failed")
        raise
    db.refresh(chat)
    logger.info("chat_created", extra={"chat_id": chat.id})
    return chat

def get_chat(db: Session, chat_id: int) -> Chat:
    chat = db.get(Chat, chat_id)
    if not chat:
        raise NotFoundError("Chat not found")
    return chat

def get_last_messages(db: Session, chat_id: int, limit: int) -> list[Message]:
    stmt = (
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
    )
    # Fetch last N messages efficiently (DESC + LIMIT) and return them
    # sorted by created_at ascending to satisfy "sorted by created_at" in API.
    messages = list(db.scalars(stmt).all())
    messages.reverse()
    return messages

def delete_chat(db: Session, chat_id: int) -> None:
    chat = get_chat(db, chat_id)
    db.delete(chat)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("delete_chat_failed", extra={"chat_id": chat_id})
        raise
    logger.info("chat_deleted", extra={"chat_id": chat_id})
