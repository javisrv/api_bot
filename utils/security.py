import os
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()
FASTAPI_PASSWORD = os.getenv('FASTAPI_PASSWORD')

def verify_api_key(x_api_key: str = Depends(APIKeyHeader(name="X-API-Key"))):
    if (x_api_key != FASTAPI_PASSWORD):
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado"
        )