import os
from utils.logger import logger
from langchain_openai  import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.callbacks import get_openai_callback
from langchain_community.vectorstores import FAISS
import json

from dotenv import load_dotenv

load_dotenv()
PATH_TEMPLATES = os.getenv('PATH_TEMPLATES')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PATH_DB = os.getenv('PATH_DB')

def get_model(model_version, model_type=None, dimensions=None, temperature=None, seed=None) -> ChatOpenAI:
    if model_type == "embeddings":
        model = OpenAIEmbeddings(model=model_version, dimensions=dimensions)
    else:
        model = ChatOpenAI(model=model_version, temperature=temperature, seed=seed)
    return model

def get_prompt(prompt_name, inputs, pydantic_object=None):
    with open(PATH_TEMPLATES, "r", encoding="utf-8") as file:
        templates = json.load(file)
    if pydantic_object:
        parser = JsonOutputParser(pydantic_object=pydantic_object)
        prompt = PromptTemplate(
            template=templates[prompt_name],
            input_variables=inputs["input"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
            )
    else:
        prompt_template = PromptTemplate.from_template(template=templates[prompt_name])
        prompt = prompt_template.format(**inputs)
    return prompt, parser if pydantic_object else None

def invoke_llm(model, prompt, parser, inputs):
    with get_openai_callback() as cb:
        if parser:
            chain = prompt | model | parser
            output = chain.invoke({"input": inputs["input"]})
            return output, cb
        else:
            output = model.invoke(prompt.format(**inputs))
            return output, cb
        
def rag(inputs):
    embeddings = get_model(model_version="text-embedding-3-small", model_type="embeddings")
    vdb = FAISS.load_local(PATH_DB, embeddings, allow_dangerous_deserialization = True)
    doc = vdb.similarity_search(inputs["input"], k = 1)
    return doc[0].page_content


def parse_tokens(inputs, cb):
    token_usage = {
        "completion_tokens": cb.completion_tokens,
        "prompt_tokens": cb.prompt_tokens,
        "total_tokens": cb.total_tokens
    }
    if "tokens_used" in inputs:
        inputs["tokens_used"]["completion_tokens"] += token_usage["completion_tokens"]
        inputs["tokens_used"]["prompt_tokens"] += token_usage["prompt_tokens"]
        inputs["tokens_used"]["total_tokens"] += token_usage["total_tokens"]
    else:
        inputs["tokens_used"] = token_usage
    return inputs

def format_order_history(messages: list) -> list:
    formatted_history = []
    
    for item in messages:
        # Formatear el mensaje del usuario y la respuesta de la IA
        formatted_history.append("HumanMessage: " + item.get("user_message", ""))
        formatted_history.append("AIMessage: " + item.get("answer", ""))
    
    reordered_history = []
    # Reordenar la lista para insertar los pares de mensajes en orden inverso
    for i in range(0, len(formatted_history), 2):
        if i + 1 < len(formatted_history):
            reordered_history.insert(0, formatted_history[i + 1])  # Respuesta de la IA
            reordered_history.insert(0, formatted_history[i])      # Mensaje del usuario
    
    return reordered_history

def edge_has_name(inputs):
    logger.debug(f"Entrando a 'edge_has_name'. Sus inputs son: {inputs["user_name"]}")
    if inputs["user_name"]:
        logger.debug("Respuesta del conditional_edge 'edge_has_name': 'request'")
        return "request"
    else:
        logger.debug("Respuesta del conditional_edge 'edge_has_name': 'end'")
        return "end"
    
def edge_has_language(inputs):
    logger.debug(f"Entrando a 'edge_has_language'. Sus inputs son: {inputs["language"]}")
    if inputs["language"]:
        logger.debug("Respuesta del conditional_edge 'edge_has_language': 'rag'")
        return "rag"
    else:
        logger.debug("Respuesta del conditional_edge 'edge_has_language': 'end'")
        return "end"
