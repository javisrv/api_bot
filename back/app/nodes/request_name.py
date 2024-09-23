import os
from dotenv import load_dotenv
from utils.logger import logger
from typing import Dict
from models.dataclasses import Name

# Cargo variables de ambiente
load_dotenv()
CHAT_TEMPERATURE = os.getenv('CHAT_TEMPERATURE')
CHAT_SEED = os.getenv('CHAT_SEED')


@staticmethod
def request_name(inputs: Dict[str, str]) -> Dict[str, str]:
    from utils.functions import CallChain
    """
    Solicita el nombre del usuario si no está presente en el diccionario 'inputs'.
    Actualiza el nombre del usuario en el diccionario de entradas ('inputs["user_name"]') si es obtenido.
    Si no se recibe un nombre claro, la respuesta en 'agent_outcome' será un mensaje alternativo pidiendo al usuario que repita su nombre.
    Registra en el log las acciones realizadas y el resultado del nodo 'request_name'.

    Args:
        inputs (Dict[str, str]): Diccionario que contiene los datos que se almacenarán en la base de datos, incluyendo la clave 'user_name'.

    Returns:
        Dict[str, str]: Diccionario 'inputs' actualizado con la información del nombre del usuario en las siguientes claves:
            - 'user_name': Nombre del usuario ingresado o identificado.
            - 'agent_outcome': La respuesta generada por el LLM. Si el nombre no se puede extraer, incluye un mensaje alternativo para solicitar el nombre nuevamente.
    Notas:
        - La función verifica si ya existe un 'user_name' en los inputs. Si no está presente, se ejecuta un prompt para solicitar el nombre.
        - Si el prompt no logra obtener el nombre, se asigna un mensaje predeterminado en 'agent_outcome'.
    """
    logger.debug("Entrando en el nodo 'request_name'.")
    if not inputs["user_name"]: # Si no tengo un nombre de usuario, entonces parseo la respuesta del usuario
        CallChain.run(inputs, prompt_name="get_name", pydantic_object=Name)
        if not inputs["agent_outcome"]["user_name"]: # Si no pude extraer el nombre de usuario, entonces es un no entendido
            inputs["agent_outcome"] = "¡Uy, Perdoname pero no te entendí! ¿Me podés decir tu nombre?"
        else:
            inputs["user_name"] = inputs["agent_outcome"]["user_name"].capitalize() # Si pude extraer un nombre, entonces lo guardo en el diccionario de 'inputs'
        logger.debug(f"Respuesta del Nodo 'request_name': {inputs["agent_outcome"]}")
    else:
        logger.debug(f"El nodo 'request_name' no hizo nada.") # Si ya tengo un nombre de usuario, paso directamente al siguiente nodo
    return inputs