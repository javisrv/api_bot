import os
import time
from typing import Dict
from utils.logger import logger
from utils.auxiliar_functions import get_prompt, get_model, parse_tokens, invoke_llm, rag
from models.dataclasses import Language, Name
from dotenv import load_dotenv

load_dotenv()
CHAT_MODEL = os.getenv('CHAT_MODEL')
TEMPERATURE = os.getenv('TEMPERATURE')
SEED = os.getenv('SEED')

class CallChain:
    @staticmethod
    def run(inputs: Dict[str, str], prompt_name: str, temperature: float=TEMPERATURE, seed: int=SEED, model_name=None, pydantic_object=None):
        start_time = time.time()
        prompt, parser = get_prompt(prompt_name, inputs, pydantic_object)
        model = get_model(model_version=CHAT_MODEL, temperature=temperature, seed=seed) #if model_name else get_model()
        output, cb = invoke_llm(model, prompt, parser, inputs)
        parse_tokens(inputs, cb)
        inputs["agent_outcome"] = output if parser else output.content
        partial_state = {prompt_name: inputs["agent_outcome"]}
        if (inputs.get('partial_states') is None):
            inputs["partial_states"] = partial_state
        else:
            inputs["partial_states"].update(partial_state)
        logger.info(f"Node {prompt_name} executed in {round(time.time() - start_time, 2)} seconds.")
        return inputs
    
    @staticmethod
    def request_name(inputs: Dict[str, str]):
        logger.debug("Entrando en 'get_name'")
        if not inputs["user_name"]:
            CallChain.run(inputs, prompt_name="get_name", pydantic_object=Name)
            if not inputs["agent_outcome"]["user_name"]:
                inputs["agent_outcome"] = "¡Uy, Perdoname pero no te entendí! ¿Me podés decir tu nombre? Puede ser un nombre fantasía si querés."
            else:
                inputs["user_name"] = inputs["agent_outcome"]["user_name"]
            logger.debug(f"Respuesta del Nodo 'get_name': {inputs["agent_outcome"]}")
        logger.debug(f"El nodo 'get_name' no hizo nada.")
        return inputs
    
    @staticmethod
    def request_language(inputs: Dict[str, str]):
        logger.debug("Entrando en 'request_language'")
        if not inputs["language"]:
            if not inputs["partial_states"]:
                CallChain.run(inputs, prompt_name="get_language", pydantic_object=Language)
                if not inputs["agent_outcome"]["language"]:
                    inputs["agent_outcome"] = "¡Uy, Perdoname pero no te entendí! ¿Me lo podés volver a escribir?"
                else:
                    inputs["input_translated"] = inputs["agent_outcome"]["translate"]
                    inputs["language"] = inputs["agent_outcome"]["language"]
            else:
                inputs["agent_outcome"] = f"¡Excelente, mucho gusto {inputs["user_name"].capitalize()}! Preguntame lo que quieras."
                partial_state = {"request_language": inputs["agent_outcome"]}
                inputs["partial_states"].update(partial_state)
            logger.debug(f"Respuesta del Nodo 'request_language': {inputs["agent_outcome"]}")
        elif not inputs["input_translated"]:
            CallChain.run(inputs, prompt_name="get_language", pydantic_object=Language)
            if not inputs["agent_outcome"]["language"]:
                inputs["agent_outcome"] = "¡Uy, Perdoname pero no te entendí! ¿Me lo podés volver a escribir?"
            else:
                inputs["input_translated"] = inputs["agent_outcome"]["translate"]
                inputs["language"] = inputs["agent_outcome"]["language"]
        logger.debug(f"El nodo 'request_language' no hizo nada.")
        return inputs
    
    @staticmethod
    def rag(inputs: Dict[str, str]):
        logger.debug("Entrando en 'rag'")
        inputs["rag"]=rag(inputs)
        logger.debug(f"Información recuperada por el RAG: {inputs["rag"]}")
        CallChain.run(inputs, prompt_name="rag")
        logger.debug(f"Respuesta del Nodo 'rag': {inputs["agent_outcome"]}")
        return inputs
    
    @staticmethod
    def personality(inputs: Dict[str, str]):
        logger.debug("Entrando en 'personality'")
        CallChain.run(inputs, prompt_name="personality")
        logger.debug(f"Respuesta del Nodo 'personality': {inputs["agent_outcome"]}")
        return inputs