import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from utils.auxiliar_functions import get_model
from dotenv import load_dotenv

load_dotenv()
PATH_DOC = os.getenv('PATH_DOC')
PATH_DB = os.getenv('PATH_DB')
EMBEDDING_NAME_MODEL = os.getenv('EMBEDDING_NAME_MODEL')
EMBEDDING_SIZE_MODEL = os.getenv('EMBEDDING_SIZE_MODEL')

def calcular_max_caracteres(texto):
    parrafos = texto.split("\n\n")
    print()
    longitudes = [len(parrafo) for parrafo in parrafos]
    return max(longitudes) + 1

def create_vdb(path_doc, model, path_db):
    print(path_doc)
    loader = Docx2txtLoader(path_doc)
    data = loader.load()
    chunk_size = calcular_max_caracteres(data[0].page_content)
    text_splitter = RecursiveCharacterTextSplitter(
       chunk_size = chunk_size,
       chunk_overlap  = 0,
       length_function = len
       )
    chunks = text_splitter.split_documents(data)
    embeddings = get_model(model_version=EMBEDDING_NAME_MODEL, model_type="embeddings", dimensions=EMBEDDING_SIZE_MODEL)
    vdb = FAISS.from_documents(chunks, embeddings)
    vdb.save_local(path_db)

if __name__ == "__main__":
    if PATH_DOC and PATH_DB:
        create_vdb(PATH_DOC, "text-embedding-3-small", PATH_DB)
    else:
        print("Las variables de entorno PATH_DOC o PATH_DB no están definidas.")