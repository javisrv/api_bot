import os
from dotenv import load_dotenv
from utils.logger import logger
from typing import Dict
from utils.auxiliar_functions import rag

# Cargo variables de ambiente
load_dotenv()
CHAT_TEMPERATURE = os.getenv('CHAT_TEMPERATURE')
CHAT_SEED = os.getenv('CHAT_SEED')


@staticmethod
def call_rag(inputs: Dict[str, str]) -> Dict[str, str]:
    from utils.functions import CallChain
    """
    Ejecuta un proceso de Recuperación de la información de la base de datos vectorial.

    Args:
        inputs (Dict[str, str]): Diccionario que contiene los datos que se almacenarán en la base de datos, incluyendo la claves 'agent_outcome'.

    Returns:
        Dict[str, str]: Diccionario 'inputs' actualizado con la siguiente clave:
            - 'agent_outcome': Respuesta generada por el LLM después de extraer información de la base de datos vectorial y procesar el prompt 'rag'.

    Efectos Colaterales:
        - Ejecuta el nodo 'rag' a través de `CallChain.run`, que genera una respuesta almacenada en 'agent_outcome'.
        - Registra en el log las acciones realizadas, incluida la información recuperada y la respuesta del nodo 'rag'.

    Notas:
        - La función utiliza el proceso RAG para recuperar información relevante basada en las entradas proporcionadas.
        - La información recuperada se almacena en 'rag', y luego se ejecuta el prompt correspondiente para generar una respuesta.
    """
    logger.debug("Entrando en el nodo 'call_rag'")
    inputs["rag"]=rag(inputs)
    CallChain.run(inputs, prompt_name="call_rag") # model_type="chat"
    logger.debug(f"Respuesta del Nodo 'call_rag': {inputs["agent_outcome"]}")
    return inputs