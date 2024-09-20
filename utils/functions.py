import os
import time
from typing import Dict
from utils.logger import logger
from utils.auxilar_functions import get_prompt, get_model, parse_tokens, invoke_llm
from models.dataclasses import Language

class CallChain:
    @staticmethod
    def run(inputs: Dict[str, str], prompt_name: str, temperature: float = 0, model_name=None, pydantic_object=None):
        start_time = time.time()
        prompt, parser = get_prompt(prompt_name, inputs, pydantic_object)
        model = get_model(model_name) if model_name else get_model()
        output, cb = invoke_llm(model, prompt, parser, inputs)
        parse_tokens(inputs, cb)
        inputs["agent_outcome"] = output if parser else output.content
        logger.info(f"Node {prompt_name} executed in {round(time.time() - start_time, 2)} seconds.")
        return inputs
    
    @staticmethod
    def get_language(inputs: Dict[str, str]):
        logger.debug("Entrando en 'detecta_idioma'")
        CallChain.run(inputs, prompt_name="get_language", temperature=0, pydantic_object=Language)
        inputs["input_translated"] = inputs["agent_outcome"]["translate"]
        inputs["language"] = inputs["agent_outcome"]["language"]
        logger.debug(f"Respuesta del Nodo 'rag': {inputs["agent_outcome"]}")
        return inputs
    
    @staticmethod
    def rag(inputs: Dict[str, str]):
        logger.debug("Entrando en 'test'")
        CallChain.run(inputs, prompt_name="rag", temperature=0)
        logger.debug(f"Respuesta del Nodo 'rag': {inputs["agent_outcome"]}")
        return inputs