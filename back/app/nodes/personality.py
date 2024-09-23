import os
from dotenv import load_dotenv
from utils.logger import logger
from typing import Dict

# Cargo variables de ambiente
load_dotenv()
CHAT_TEMPERATURE = os.getenv('CHAT_TEMPERATURE')
CHAT_SEED = os.getenv('CHAT_SEED')


@staticmethod
def personality(inputs: Dict[str, str]) -> Dict[str, str]:
    from utils.functions import CallChain
    """
    Ejecuta el nodo 'personality' para generar una respuesta relacionada con la personalidad del LLM y actualiza la clave 'agent_outcome'.

    Args:
        inputs (Dict[str, str]): Diccionario que contiene los datos que se almacenarán en la base de datos, incluyendo la claves 'agent_outcome'.

    Returns:
        Dict[str, str]: Diccionario 'inputs' actualizado con la respuesta generada por el nodo 'personality' en la clave:
            - 'agent_outcome': Respuesta generada relacionada con la personalidad del LLM.

    Efectos Colaterales:
        - Ejecuta el nodo 'personality' a través de `CallChain.run`, que genera una respuesta almacenada en 'agent_outcome'.
        - Registra en el log las acciones realizadas y la respuesta generada por el nodo 'personality'.

    Notas:
        - El nodo 'personality' es ejecutado para generar una respuesta relevante relacionada con la personalidad del LLM.
    """
    logger.debug("Entrando en el nodo 'personality'")
    logger.debug(f"La respuesta debe ser en el idioma: '{inputs['language']}'")
    if inputs["language"] == "español":
        CallChain.run(inputs, prompt_name="personality_esp")
    else:
        CallChain.run(inputs, prompt_name="personality")
    logger.debug(f"Respuesta del Nodo 'personality': {inputs["agent_outcome"]}")
    return inputs