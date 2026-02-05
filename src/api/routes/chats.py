from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.schemas.chat import ChatCreate, ChatDetailResponse, ChatResponse
from src.schemas.message import MessageCreate, MessageResponse
from src.services import chat_service, message_service

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(payload: ChatCreate, db: Session = Depends(get_db)) -> ChatResponse:
    chat = chat_service.create_chat(db, payload.title)
    return ChatResponse.model_validate(chat)

@router.get("/{chat_id}", response_model=ChatDetailResponse)
def get_chat_with_messages(
    chat_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ChatDetailResponse:
    try:
        chat = chat_service.get_chat(db, chat_id)
    except chat_service.NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    messages = chat_service.get_last_messages(db, chat_id, limit)

    return ChatDetailResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        messages=[MessageResponse.model_validate(m) for m in messages],
    )

@router.post("/{chat_id}/messages/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    chat_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
) -> MessageResponse:
    try:
        msg = message_service.create_message(db, chat_id, payload.text)
    except chat_service.NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return MessageResponse.model_validate(msg)

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(chat_id: int, db: Session = Depends(get_db)) -> None:
    try:
        chat_service.delete_chat(db, chat_id)
    except chat_service.NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None
