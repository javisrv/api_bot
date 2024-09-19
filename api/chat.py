from models.dataclasses import ChatRequest, ChatResponse
from db.orm.orm import db_engine
from db.orm.orm_models import UsrSession, UsrMessages
from utils.logger import logger


def get_answer(request: ChatRequest):
    logger.debug("Entrando en 'get_answer'")
    if not request.session_id:
        session = UsrSession()
        request.session_id = session.id
        db_engine.save(session)
    else:
        pass 
    usr_messages = UsrMessages(
            session_id=request.session_id,
            user_message=request.input,
            answer="hola Javier!",
            intent="saludo",
            tokens_used={"enviados": 123, "retornados": 256, "totales": 379},
            state={"primer saludo": "holaaaa"}
            )
    db_engine.save(usr_messages)

    return ChatResponse(
            session_id=request.session_id,
            respuesta="hola Javier!"
        )