import os
from dotenv import load_dotenv
from utils.logger import logger
import time
from typing import Dict
from utils.auxiliar_functions import get_prompt, get_model, parse_tokens, invoke_llm

# Cargo variables de ambiente
load_dotenv()
CHAT_TEMPERATURE = os.getenv('CHAT_TEMPERATURE')
CHAT_SEED = os.getenv('CHAT_SEED')


@staticmethod
def run(inputs: Dict[str, str], 
            prompt_name: str, 
            model_type: str="chat",
            temperature: float=CHAT_TEMPERATURE, 
            seed: int=CHAT_SEED,
            pydantic_object=None,
            ) -> Dict[str, str]:
        """
        Ejecuta un prompt usando un LLM, procesa el resultado y actualiza el diccionario 'inputs' con la respuesta del modelo.

        Args:
            inputs (Dict[str, str]): Diccionario que contiene los datos que se almacenarán en la base de datos.
            prompt_name (str): Identificador del prompt que se va a ejecutar.
            temperature (float, opcional): Temperatura del LLM.
            seed (int, opcional): Semilla aleatoria para asegurar la reproducibilidad del comportamiento del LLM.
            model (str, opcional): Versión específica del modelo a usar. Si es `None`, se usa un modelo preconfigurado.
            pydantic_object (opcional): Objeto Pydantic utilizado para la validación dinámica de entradas y el parseo.

        Returns:
            Dict[str, str]: Diccionario 'inputs' actualizado con nuevas claves:
                - 'agent_outcome': La respuesta generada por el modelo.
                - 'partial_states': Un diccionario con actualizaciones de estado parcial para el prompt actual.
            
        Efectos Colaterales:
            - Actualiza las claves 'agent_outcome' y 'partial_states' en el diccionario `inputs`.
            - Registra en el log el tiempo de ejecución del prompt.
        
        Notas:
            - La función recupera el prompt basado en `prompt_name`, lo ejecuta a través de un modelo de lenguaje y procesa la salida del modelo.
            - La salida se parsea y se incorpora de vuelta en `inputs` bajo la clave 'agent_outcome'.
            - Se actualiza o inicializa la clave 'partial_states' en `inputs` si no está presente.
        """
        logger.debug("Entrando en la llamada al LLM.")
        start_time = time.time()
        prompt, parser = get_prompt(inputs, prompt_name, pydantic_object)
        model = get_model(model_type=model_type,temperature=temperature, seed=seed)
        output, cb = invoke_llm(model, prompt, parser, inputs)
        parse_tokens(inputs, cb)
        inputs["agent_outcome"] = output if parser else output.content
        partial_state = {prompt_name: inputs["agent_outcome"]}
        if (inputs.get('partial_states') is None):
            inputs["partial_states"] = partial_state
        else:
            inputs["partial_states"].update(partial_state)
        logger.info(f"LLamada al LLM con el prompt: '{prompt_name}' ejecutada en {round(time.time() - start_time, 2)} segundos.")
        logger.debug(f"Respuesta del LLM: '{inputs["agent_outcome"]}'")
        return inputs