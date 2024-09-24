import os
from dotenv import load_dotenv
import time
from utils.logger import logger
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.auxiliar_functions import get_model

load_dotenv()
PATH_DOC = os.getenv('PATH_DOC')
PATH_DB = os.getenv('PATH_DB')
EMBEDDING_NAME_MODEL = os.getenv('EMBEDDING_NAME_MODEL')
EMBEDDING_SIZE_MODEL = os.getenv('EMBEDDING_SIZE_MODEL')


def calcular_max_caracteres(texto):
    """
    Calcula la longitud máxima de los párrafos en un texto.

    Esta función divide el texto en párrafos utilizando dos saltos de línea como delimitador 
    y devuelve la longitud del párrafo más largo, incrementada en uno.

    Parámetros:
        texto (str): El texto que se va a analizar, el cual puede contener múltiples párrafos.

    Retorno:
        int: La longitud del párrafo más largo más uno.
    """
    parrafos = texto.split("\n\n")
    print()
    longitudes = [len(parrafo) for parrafo in parrafos]
    return max(longitudes) + 1

def create_vdb(path_doc, path_db):
    """
    Crea y guarda una base de datos vectorial a partir de un documento.

    Esta función carga un documento desde la ruta especificada, divide su contenido en 
    fragmentos utilizando un tamaño de chunk calculado y luego crea una base de datos 
    vectorial utilizando embeddings del modelo especificado. Finalmente, la base de datos 
    se guarda en la ruta proporcionada.

    Parámetros:
        path_doc (str): La ruta al documento que se va a cargar.
        model (str): El tipo de modelo que se va a utilizar para generar embeddings.
        path_db (str): La ruta donde se guardará la base de datos vectorial.

    Retorno:
        None: La función no devuelve ningún valor. Los resultados se guardan en el sistema de archivos.

    Excepciones:
        Puede lanzar excepciones si hay errores en la carga del documento o en la creación de la base de datos.
    """
    start_time = time.time()
    logger.info("Creando base de datos vectorial.")
    loader = Docx2txtLoader(path_doc)
    data = loader.load()
    chunk_size = calcular_max_caracteres(data[0].page_content)
    text_splitter = RecursiveCharacterTextSplitter(
       chunk_size = chunk_size,
       chunk_overlap  = 0,
       length_function = len
       )
    chunks = text_splitter.split_documents(data)
    embeddings = get_model(model_type="embeddings")
    vdb = FAISS.from_documents(chunks, embeddings)
    vdb.save_local(path_db)
    return logger.info(f"Base de datos vectorial creada en {round(time.time() - start_time, 2)} segundos.")

if __name__ == "__main__":
    if PATH_DOC and PATH_DB:
        create_vdb(PATH_DOC, PATH_DB)
    else:
        logger.info(f"Las variables de entorno PATH_DOC o PATH_DB no están definidas.")