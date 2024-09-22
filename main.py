import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from rutas.chat import router_chat
from utils.security import verify_api_key

load_dotenv()
FASTAPI_NAME = os.getenv('FASTAPI_NAME')
FASTAPI_VERSION = os.getenv('FASTAPI_VERSION')


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

app = FastAPI(
    title=FASTAPI_NAME,
    version=FASTAPI_VERSION,
    dependencies=[Depends(verify_api_key)]
)

app.include_router(router_chat)

@app.get("/health")
def session() -> str:
    return "OK"