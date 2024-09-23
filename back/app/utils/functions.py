import os
from dotenv import load_dotenv
from nodes.call_rag import call_rag
from nodes.personality import personality
from nodes.request_language import request_language
from nodes.request_name import request_name
from nodes.run import run
from typing import Dict


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
            pydantic_object=None) -> Dict[str, str]:
        return run(inputs, prompt_name, model_type, temperature, seed, pydantic_object)

    @staticmethod
    def request_name(inputs: Dict[str, str]) -> Dict[str, str]:
        return request_name(inputs)
    
    @staticmethod
    def request_language(inputs: Dict[str, str]) -> Dict[str, str]:
        return request_language(inputs)
    
    @staticmethod
    def call_rag(inputs: Dict[str, str]) -> Dict[str, str]:
        return call_rag(inputs)
    
    @staticmethod
    def personality(inputs: Dict[str, str]) -> Dict[str, str]:
        return personality(inputs)