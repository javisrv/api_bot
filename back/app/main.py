import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from utils.logger import logger
from db.vdb.vector_db import create_vdb
from rutas.chat import router_chat
from utils.security import verify_api_key

load_dotenv()
FASTAPI_NAME = os.getenv('FASTAPI_NAME')
FASTAPI_VERSION = os.getenv('FASTAPI_VERSION')
PATH_DOC = os.getenv('PATH_DOC')
PATH_DB = os.getenv('PATH_DB')

"""
Configuración de la aplicación FastAPI.

Este script inicializa la aplicación FastAPI con el título 'Challenge Pi Consulting' y la versión '0.0.1'.
Incluye una dependencia para verificar la clave API en todas las solicitudes y registra
el router para el chat. Además, define un endpoint de verificación de salud.

Atributos:
    app (FastAPI): La instancia de la aplicación FastAPI inicializada con un título,
        versión y una dependencia para verificar la clave API.

Rutas:
    - /health (GET): Devuelve "OK" como una verificación simple de salud para confirmar
        que el servicio está funcionando.

Funciones:
    session() -> str: Un endpoint de verificación de salud que devuelve la cadena "OK".

"""
faiss_file = os.path.exists(os.path.join(os.getcwd(), PATH_DB,'index.faiss'))
pkl_file = os.path.exists(os.path.join(os.getcwd(), PATH_DB,'index.pkl'))
logger.debug(f"Directorio de 'index.faiss': {os.path.join(os.getcwd(), PATH_DB,'index.faiss')}")
logger.debug(f"Directorio de 'index.pkl': {os.path.join(os.getcwd(), PATH_DB,'index.pkl')}")

if not faiss_file or not pkl_file:
    create_vdb(PATH_DOC, PATH_DB)
else:
    logger.info(f"La base de datos vectorial ya estaba creada.")

app = FastAPI(
    title=FASTAPI_NAME,
    version=FASTAPI_VERSION,
    dependencies=[Depends(verify_api_key)]
)

app.include_router(router_chat)

@app.get("/health")
def session() -> str:
    return "OK"