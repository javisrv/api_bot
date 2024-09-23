import os
from dotenv import load_dotenv
import json
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from tenacity import timeout
from typing import Dict, Union, Any
from langchain_openai  import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.callbacks import get_openai_callback
from langchain_community.vectorstores import FAISS
from utils.logger import logger

load_dotenv()
PATH_TEMPLATES = os.getenv('PATH_TEMPLATES')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PATH_DB = os.getenv('PATH_DB')
CHAT_NAME_MODEL = os.getenv('CHAT_NAME_MODEL')
EMBEDDING_NAME_MODEL = os.getenv('EMBEDDING_NAME_MODEL')
EMBEDDING_SIZE_MODEL = os.getenv('EMBEDDING_SIZE_MODEL')


def get_model(model_type, temperature=None, seed=None, model_chat=CHAT_NAME_MODEL, model_embedding=EMBEDDING_NAME_MODEL, dimensions=EMBEDDING_SIZE_MODEL) -> Union[ChatOpenAI, OpenAIEmbeddings]:
    """
    Obtiene un modelo de chat/embedding según el tipo de 'model_type' especificado.

    Args:
        model_type (str): Tipo de modelo a obtener. Puede ser "embeddings" o un modelo de "chat".
        temperature (float, opcional): Parámetro que controla la creatividad del modelo de "chat". Por defecto es None.

    Returns:
        ChatOpenAI: Instancia del modelo seleccionado. Si el tipo es "embeddings", se retorna un modelo de embeddings; de lo contrario, un modelo de chat.

    Efectos Colaterales:
        - Crea una instancia de `OpenAIEmbeddings` si `model_type` es "embeddings".
        - Crea una instancia de `ChatOpenAI` si se requiere un modelo de chat, configurando el nombre del modelo, la temperatura y la semilla para la generación.

    Notas:
        - El modelo de embeddings utiliza el nombre y el tamaño de los embeddings definidos en las constantes `EMBEDDING_NAME_MODEL` y `EMBEDDING_SIZE_MODEL`.
        - El modelo de chat utiliza el nombre del modelo y la semilla definidos en las constantes `CHAT_NAME_MODEL` y `CHAT_SEED`.
    """
    logger.debug(f"Entrando en la función 'get_model'.")
    if model_type == "embeddings":
        model = OpenAIEmbeddings(model=model_embedding, dimensions=dimensions)
    else:
        model = ChatOpenAI(model=model_chat, temperature=temperature, seed=seed)
    logger.debug(f"Modelo de '{model_type}' instanciado.")
    return model


def get_prompt(inputs: dict, prompt_name: str, pydantic_object=None) -> tuple:
    """
    Carga una plantilla de prompt desde un archivo JSON y la formatea con los valores de entrada proporcionados.

    Args:
        prompt_name (str): El nombre de la plantilla de prompt a cargar.
        inputs (Dict[str, str]): Diccionario que contiene los datos que se almacenarán en la base de datos.
        pydantic_object (Optional[Type[PydanticModel]], optional): Un modelo de Pydantic opcional para parsear la salida JSON.

    Returns:
        Tuple[str, Optional[JsonOutputParser]]:
            - str: La plantilla de prompt formateada.
            - Optional[JsonOutputParser]: Un objeto JsonOutputParser si se proporciona un pydantic_object, de lo contrario None.
    """
    logger.debug(f"Entrando en la función 'get_prompt'.")
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
    logger.debug(f"Prompt instanciado.")
    return prompt, parser if pydantic_object else None


@retry(stop=stop_after_attempt(2), wait=wait_fixed(2), reraise=True)
@timeout(30)  # Límite de tiempo de 30 segundos por intento
def invoke_llm(model: ChatOpenAI, prompt: str, parser: JsonOutputParser, inputs: dict) -> tuple:
    """
    Invoca un LLM con un prompt dado y procesa la salida mediante un parser opcional.

    Args:
        model: El modelo de lenguaje a invocar.
        prompt: La plantilla de prompt que se utilizará para generar la entrada del modelo.
        parser: Un parser opcional que procesa la salida del modelo.
        inputs (Dict[str, Any]): Un diccionario que contiene las variables de entrada necesarias para el prompt.

    Returns:
        Tuple[Any, Any]:
            - output: La salida generada por el modelo de lenguaje.
            - cb: Un objeto de callback que proporciona información sobre la invocación (como el uso de tokens).
    """
    logger.debug(f"Entrando en la función 'invoke_llm'.")
    
    try:
        with get_openai_callback() as cb:
            if parser:
                chain = prompt | model | parser
                output = chain.invoke({"input": inputs["input"]})
                logger.debug(f"Respuesta del LLM instanciada.")
                return output, cb
            else:
                output = model.invoke(prompt.format(**inputs))
                logger.debug(f"Respuesta del LLM instanciada.")
                return output, cb
    except RetryError as e:
        logger.error(f"Fallo tras varios intentos: {e}")
        raise e  # Lanza el error tras agotar los intentos
    except Exception as e:
        logger.error(f"Error al invocar el LLM: {e}")
        raise e


def rag(inputs: dict) -> str:
    """
    Realiza una búsqueda de documentos similar utilizando un modelo de embeddings y una base de datos FAISS.

    Args:
        inputs (Dict[str, Any]): Un diccionario que contiene la entrada para la búsqueda, específicamente
                                  la clave "input" con el texto a buscar.

    Returns:
        str: El contenido de la página del documento más similar encontrado en la base de datos.
    """
    logger.debug(f"Entrando en la función 'rag'.")
    embeddings = get_model(model_type="embeddings")
    vdb = FAISS.load_local(PATH_DB, embeddings, allow_dangerous_deserialization = True)
    doc = vdb.similarity_search(inputs["input"], k = 1)
    logger.debug(f"Información recuperada por el RAG: '{doc[0].page_content}'")
    return doc[0].page_content


def parse_tokens(inputs: Dict[str, Any], cb) -> Dict[str, Any]:
    """
    Actualiza el diccionario 'inputs' con el uso de tokens a partir de un objeto de callback en la clave 'tokens_used'.

    Args:
        inputs (Dict[str, str]): Diccionario que contiene los datos que se almacenarán en la base de datos, entre ellos la clave 'tokens_used'.
        cb: Un objeto de callback que proporciona información sobre los tokens usados en la invocación.

    Returns:
        Dict[str, Any]: El diccionario de entrada actualizado con la información del uso de tokens.
    """
    logger.debug(f"Entrando en la función 'parse_tokens'.")
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
    logger.debug(f"Tokens calculados: {inputs['tokens_used']}")
    return inputs


def format_order_history(messages: list) -> list:
    """
    Formatea y reordena el historial de mensajes entre un usuario y una IA.

    Args:
        messages (list): Una lista de diccionarios, donde cada diccionario contiene
                         un mensaje de usuario y la respuesta de la IA bajo las claves
                         "user_message" y "answer".

    Returns:
        list: Una lista formateada que alterna los mensajes del usuario y las respuestas
              de la IA, ordenados de manera que las respuestas de la IA aparecen antes
              de los mensajes del usuario en la lista final.
    """
    logger.debug(f"Entrando en la función 'format_order_history'.")
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
    logger.debug(f"Historial ordenado y formateado.")
    return reordered_history


def edge_has_name(inputs) -> str:
    """
    Evalúa si el usuario ha proporcionado un nombre y devuelve una respuesta basada en esa evaluación.

    Args:
        inputs (Dict[str, Any]): Un diccionario que contiene la clave "user_name" con el nombre del usuario.

    Returns:
        str: Devuelve "request" si se proporciona un nombre, de lo contrario devuelve "end".
    """
    logger.debug(f"Entrando a 'edge_has_name'. Sus inputs son: {inputs["user_name"]}")
    if inputs["user_name"]:
        logger.debug("Respuesta del conditional_edge 'edge_has_name': 'request'")
        return "request"
    else:
        logger.debug("Respuesta del conditional_edge 'edge_has_name': 'end'")
        return "end"
    

def edge_has_language(inputs) -> str:
    """
    Evalúa si el usuario ha proporcionado un idioma y devuelve una respuesta basada en esa evaluación.

    Args:
        inputs (Dict[str, Any]): Un diccionario que contiene la clave "language" con el idioma del usuario.

    Returns:
        str: Devuelve "rag" si se proporciona un idioma, de lo contrario devuelve "end".
    """
    logger.debug(f"Entrando a 'edge_has_language'. Sus inputs son: {inputs["language"]}")
    if inputs["language"]:
        logger.debug("Respuesta del conditional_edge 'edge_has_language': 'rag'")
        return "rag"
    else:
        logger.debug("Respuesta del conditional_edge 'edge_has_language': 'end'")
        return "end"