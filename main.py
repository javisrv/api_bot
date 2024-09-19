import os
from fastapi import FastAPI, Depends
from rutas.chat import router_chat
from dotenv import load_dotenv
from utils.security import verify_api_key

load_dotenv()
FASTAPI_NAME = os.getenv('FASTAPI_NAME')
FASTAPI_VERSION = os.getenv('FASTAPI_VERSION')

app = FastAPI(
    title=FASTAPI_NAME,
    version=FASTAPI_VERSION,
    dependencies=[Depends(verify_api_key)]
)

app.include_router(router_chat)

@app.get("/health")
def session() -> str:
    return "OK"