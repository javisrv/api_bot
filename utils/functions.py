import os
from dotenv import load_dotenv
from utils.logger import logger
import time
from typing import Dict
from utils.auxiliar_functions import get_prompt, get_model, parse_tokens, invoke_llm, rag
from models.dataclasses import Language, Name

# Cargo variables de ambiente
load_dotenv()
CHAT_TEMPERATURE = os.getenv('CHAT_TEMPERATURE')
CHAT_SEED = os.getenv('CHAT_SEED')


class CallChain:
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
        logger.debug("Entrando en el 'run'.")
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
        logger.info(f"Node {prompt_name} ejecutado en {round(time.time() - start_time, 2)} segundos.")
        logger.debug(f"Respuesta de 'run' {inputs["agent_outcome"]}")
        return inputs
    
    @staticmethod
    def request_name(inputs: Dict[str, str]) -> Dict[str, str]:
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
                inputs["agent_outcome"] = "¡Uy, Perdoname pero no te entendí! ¿Me podés decir tu nombre? Puede ser un nombre fantasía si querés."
            else:
                inputs["user_name"] = inputs["agent_outcome"]["user_name"] # Si pude extraer un nombre, entonces lo guardo en el diccionario de 'inputs'
            logger.debug(f"Respuesta del Nodo 'request_name': {inputs["agent_outcome"]}")
        else:
            logger.debug(f"El nodo 'request_name' no hizo nada.") # Si ya tengo un nombre de usuario, paso directamente al siguiente nodo
        return inputs
    
    @staticmethod
    def request_language(inputs: Dict[str, str]) -> Dict[str, str]:
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
    
    @staticmethod
    def rag(inputs: Dict[str, str]) -> Dict[str, str]:
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
        logger.debug("Entrando en el nodo 'rag'")
        inputs["rag"]=rag(inputs)
        CallChain.run(inputs, prompt_name="rag") # model_type="chat"
        logger.debug(f"Respuesta del Nodo 'rag': {inputs["agent_outcome"]}")
        return inputs
    
    @staticmethod
    def personality(inputs: Dict[str, str]) -> Dict[str, str]:
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