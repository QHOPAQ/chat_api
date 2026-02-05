import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from src.api.routes.chats import router as chats_router
from src.api.routes.health import router as health_router
from src.core.logging import configure_logging

configure_logging()
logger = logging.getLogger("app")

app = FastAPI(title="Chat API", version="1.0.0")
app.include_router(health_router)
app.include_router(chats_router)

@app.exception_handler(SQLAlchemyError)
def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("db_error", extra={"path": str(request.url.path)})
    return JSONResponse(status_code=500, content={"detail": "Database error"})
