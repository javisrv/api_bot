from models.dataclasses import ChatRequest, ChatResponse
from db.orm.orm import db_engine
from db.orm.orm_models import UsrSession, UsrMessages
from utils.auxiliar_functions import format_order_history
from api.graph import load_graph
from utils.logger import logger


def get_answer(request: ChatRequest):
    logger.debug("Entrando en 'get_answer'")
    if not request.session_id:
        session = UsrSession()
        request.session_id = session.id
        db_engine.save(session)
        user_name = None
        language = None
        history_message = [{"HumanMessage": "", 
                            "AIMessage": 
                                        """
                                        ¡Hola! Soy tu asistente conversacional para el challenge de Pi Consulting 😊. 
                                        Estoy para ayudarte a responder cualquier duda que tengas. 
                                        ¡Preguntame todo lo que necesites! 
                                        Para empezar me encantaría que me dijeras tu nombre o pseudónimo.
                                        """
                            }]
    else:
        logger.info("Session %s requested.", request.session_id)
        messages = db_engine.retrieve_history(request.session_id, UsrMessages)
        if messages:
            history_message = format_order_history(messages)
        else:
            history_message = UsrMessages().to_dict() 
        last_message = db_engine.get_last_message_dict()
        user_name = last_message["user_name"]
        language = last_message["language"]
    inputs = {
        "input": request.input,
        "input_translated": None,
        "user_name": user_name,
        "chat_history": history_message,
        "language": language,
        "partial_states": None
    }

    answer = load_graph().invoke(inputs)
    logger.info(f"Respuesta final del bot: {answer['agent_outcome']}")
    usr_messages = UsrMessages(
            session_id=request.session_id,
            user_name=answer["user_name"],
            user_message=answer["input"],
            answer=answer["agent_outcome"],
            language=answer["language"],
            tokens_used=answer["tokens_used"],
            state=answer["partial_states"]
            )
    db_engine.save(usr_messages)

    return ChatResponse(
            session_id=request.session_id,
            respuesta=answer["agent_outcome"]
        )