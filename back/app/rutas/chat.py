import time
from fastapi import APIRouter
from api.chat import get_answer
from models.dataclasses import ChatRequest, ChatResponse
from utils.logger import logger

"""
Ruta para el manejo de interacciones de chat.

Este módulo define una ruta de FastAPI para manejar las interraciones con el LLM. 
Utiliza la clase `ChatRequest` para recibir los datos de entrada y la clase 
`ChatResponse` para la respuesta.

Atributos:
    router_chat (APIRouter): La ruta configurada con el prefijo "/chat".

Rutas:
    - /chat (POST): Endpoint que procesa una solicitud de chat. Recibe un objeto de tipo 
      `ChatRequest` y devuelve un `ChatResponse`.

Funciones:
    interact(req: ChatRequest): Procesa las interraciones con el LLM utilizando la función `get_answer` 
    y registra el tiempo de procesamiento. Devuelve la respuesta del chat.
    
Parámetros:
    req (ChatRequest): El objeto de solicitud que contiene los datos del chat.

Retorno:
    ChatResponse: La respuesta procesada del chat.
"""

router_chat = APIRouter(prefix="/chat")

@router_chat.post("/chat", response_model=ChatResponse)
def interact(req: ChatRequest):
    start_time = time.time()
    res = get_answer(req)
    logger.info(f"Interacción con ID '{res.session_id}' procesada en {round(time.time() - start_time, 2)} segundos.")
    return res