import os
from dotenv import load_dotenv
from utils.logger import logger
from typing import Dict
from models.dataclasses import Language

# Cargo variables de ambiente
load_dotenv()
CHAT_TEMPERATURE = os.getenv('CHAT_TEMPERATURE')
CHAT_SEED = os.getenv('CHAT_SEED')


@staticmethod
def request_language(inputs: Dict[str, str]) -> Dict[str, str]:
    from utils.functions import CallChain
    """
    Extrae el idioma del mensaje del usuario si no está presente en los datos de entrada y traduce la entrada al español si es necesario.

    Args:
        inputs (Dict[str, str]): Diccionario que contiene los datos que se almacenarán en la base de datos, incluyendo la claves 'language' e 'input_translated'.

    Returns:
        Dict[str, str]: Diccionario 'inputs' actualizado con la información del idioma del usuario y la traducción de la entrada en las siguientes claves:
            - 'language': Idioma detectado del mensaje del usuario.
            - 'input_translated': Texto del usuario traducido al español.
            - 'agent_outcome': La respuesta generada por el LLM. Si el idioma no puede extraerse, incluye un mensaje solicitando al usuario que repita la respuesta.
            - 'partial_states': Diccionario actualizado con el estado parcial después de procesar el idioma.

    Efectos Colaterales:
        - Actualiza las claves 'language' e 'input_translated' en el diccionario de 'inputs' si se obtienen del LLM.
        - Si el idioma no se puede identificar, 'agent_outcome' contendrá un mensaje solicitando al usuario que repita su respuesta.
        - Actualiza la clave 'partial_states' con el estado parcial generado.
        - Registra en el log las acciones realizadas y el resultado del nodo 'request_language'.

    Notas:
        - Si la clave 'language' no está presente, se ejecuta un prompt para identificar el idioma del usuario.
        - Si ya se ha ejecutado previamente este nodo, se actualiza 'partial_states' con un mensaje de saludo.
        - Si la entrada no está traducida ('input_translated'), se vuelve a ejecutar el prompt para obtener el idioma y traducir la entrada.
    """
    logger.debug("Entrando en el nodo 'request_language'")
    if not inputs["language"]: # Si no tengo un idioma
        if not inputs["partial_states"]: # Si no hubo interacción en el nodo 'request_name', entonces parseo la respuesta del usuario
            CallChain.run(inputs, prompt_name="get_language", pydantic_object=Language)
            if not inputs["agent_outcome"]["language"]: # Si no pude extraer un idioma, entonces es un no entendido
                inputs["agent_outcome"] = "¡Uy, Perdoname pero no te entendí! ¿Me lo podés volver a escribir?"
            else: # Si pude extraer un idioma y mensaje traducidos al español, entonces los guardo en el diccionario de 'inputs'
                inputs["input_translated"] = inputs["agent_outcome"]["translate"]
                inputs["language"] = inputs["agent_outcome"]["language"].lower()
        else: # Si hubo interacción en el nodo 'request_name' entonces solicito al usuario un mensaje
            inputs["agent_outcome"] = f"¡Excelente, mucho gusto {inputs["user_name"].capitalize()}! Preguntame lo que quieras."
            partial_state = {"request_language": inputs["agent_outcome"]}
            inputs["partial_states"].update(partial_state)
        logger.debug(f"Respuesta del Nodo 'request_language': {inputs["agent_outcome"]}")
    elif not inputs["input_translated"]: # Si tengo idioma, parseo el mensaje la respuesta del usuario
        CallChain.run(inputs, prompt_name="get_language", pydantic_object=Language)
        if not inputs["agent_outcome"]["language"]: # Si no pude extraer un idioma, entonces es un no entendido
            inputs["agent_outcome"] = "¡Uy, Perdoname pero no te entendí! ¿Me lo podés volver a escribir?"
        else: # Si pude extraer un idioma y mensaje traducidos al español, entonces los guardo en el diccionario de 'inputs'
            inputs["input_translated"] = inputs["agent_outcome"]["translate"]
            inputs["language"] = inputs["agent_outcome"]["language"].lower()
    else:
        logger.debug(f"El nodo 'request_language' no hizo nada.")
    return inputs