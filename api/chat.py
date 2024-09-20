from models.dataclasses import ChatRequest, ChatResponse
from db.orm.orm import db_engine
from db.orm.orm_models import UsrSession, UsrMessages
from api.graph import load_graph
from utils.logger import logger


def get_answer(request: ChatRequest):
    logger.debug("Entrando en 'get_answer'")
    if not request.session_id:
        session = UsrSession()
        request.session_id = session.id
        db_engine.save(session)
    else:
        pass 
    
    inputs = {
        "input": request.input
    }

    answer = load_graph().invoke(inputs)
    logger.info(f"Respuesta final del bot: {answer['agent_outcome']}")
    usr_messages = UsrMessages(
            session_id=request.session_id,
            user_message=answer["input"],
            answer=answer["agent_outcome"],
            language=answer["language"],
            tokens_used=answer["tokens_used"],
            state={"primer saludo": "holaaaa"}
            )
    db_engine.save(usr_messages)

    return ChatResponse(
            session_id=request.session_id,
            respuesta=answer["agent_outcome"]
        )