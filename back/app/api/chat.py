from api.graph import load_graph
from db.orm.orm import db_engine
from db.orm.orm_models import UsrSession, UsrMessages
from models.dataclasses import ChatRequest, ChatResponse
from utils.auxiliar_functions import format_order_history
from utils.logger import logger


def get_answer(request: ChatRequest) -> ChatResponse:
    """
    Procesa una solicitud de interacción con el LLM y genera una respuesta.

    Esta función maneja la lógica para procesar una solicitud de chat. Si no existe una sesión previa, 
    crea una nueva y genera un mensaje de bienvenida. Si la sesión ya existe, recupera el historial de mensajes 
    y utiliza los datos del último mensaje para personalizar la respuesta.

    Parámetros:
        request (ChatRequest): El objeto que contiene los detalles de la solicitud del chat, 
        incluyendo el ID de la sesión y el mensaje del usuario.

    Retorno:
        ChatResponse: Un objeto que contiene el ID de la sesión y la respuesta generada por el bot.
    """
    logger.debug("Entrando en la función 'get_answer'.")
    # Si no existe la sesión, entonces se crea una.
    if not request.session_id:
        session = UsrSession()
        request.session_id = session.id
        logger.info("Sesión con ID %s creada.", request.session_id)
        db_engine.save(session)
        user_name = None
        language = None
        history_message = [{"HumanMessage": "", 
                            "AIMessage": 
                                        """
                                        ¡Hola! Soy tu asistente conversacional para el challenge de Pi Consulting 😊. 
                                        Estoy para ayudarte a responder cualquier duda que tengas. 
                                        ¡Preguntame todo lo que necesites! 
                                        Para empezar me encantaría que me dijeras tu nombre.
                                        """
                            }]
    # Si existe la sesión, se recuperan los datos almmacenados hasta el momento
        # en conjunto con el historial de los últimos 5 mensajes. 
    else:
        logger.info("Sesión con ID %s recuperada.", request.session_id)
        messages = db_engine.retrieve_history(request.session_id, UsrMessages)
        if messages:
            history_message = format_order_history(messages)
        else:
            history_message = UsrMessages().to_dict() 
        last_message = db_engine.get_last_message_dict()
        user_name = last_message["user_name"]
        language = last_message["language"]

    inputs = {
        "input": request.question,
        "input_translated": None,
        "user_name": user_name,
        "chat_history": history_message,
        "language": language,
        "partial_states": None
    }

    logger.debug(f"Entrando en el flujo de nodos.")
    try:
        answer = load_graph().invoke(inputs)
        usr_messages = UsrMessages(
            session_id=request.session_id,
            user_name=answer["user_name"],
            user_message=answer["input"],
            answer=answer["agent_outcome"],
            language=answer["language"],
            tokens_used=answer["tokens_used"],
            state=answer["partial_states"]
            )
        logger.debug(f"Guardando datos en la tabla 'messages'")
        db_engine.save(usr_messages)

    except Exception as e:
        logger.error(f"Error al invocar el LLM: {e}")
        answer = inputs
        answer["agent_outcome"] = "Perdón, tuvimos un problema técnico. Por favor, intentá más tarde." 
    
    logger.debug(f"Respuesta final del bot: {answer['agent_outcome']}")
    
    return ChatResponse(
            session_id=request.session_id,
            respuesta=answer["agent_outcome"]
        )