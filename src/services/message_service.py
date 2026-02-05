import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from src.models.message import Message
from src.services.chat_service import get_chat, NotFoundError

logger = logging.getLogger("message_service")

def create_message(db: Session, chat_id: int, text: str) -> Message:
    get_chat(db, chat_id)
    msg = Message(chat_id=chat_id, text=text)
    db.add(msg)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("create_message_failed", extra={"chat_id": chat_id})
        raise
    db.refresh(msg)
    logger.info("message_created", extra={"chat_id": chat_id, "message_id": msg.id})
    return msg
