import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

# Cargo variables de ambiente
load_dotenv()
FASTAPI_PASSWORD = os.getenv('FASTAPI_PASSWORD')


def verify_api_key(x_api_key: str = Depends(APIKeyHeader(name="X-API-Key"))):
    """
    Verifica la clave API proporcionada contra un valor almacenado en las variables de entorno.

    Esta función utiliza la inyección de dependencias de FastAPI para extraer la clave API 
    de los encabezados de la solicitud (específicamente, el encabezado "X-API-Key"). Luego 
    compara la clave con el valor preconfigurado almacenado en la variable de entorno 
    `FASTAPI_PASSWORD`.

    Args:
        x_api_key (str): La clave API extraída del encabezado de la solicitud "X-API-Key".

    Raises:
        HTTPException: Si la clave API proporcionada no coincide con el valor esperado, 
        se lanza un error 403 (Prohibido) con el detalle "Acceso denegado".

    Returns:
        None: Si la clave API es válida, la solicitud se permite continuar sin lanzar una excepción.
    """
    if (x_api_key != FASTAPI_PASSWORD):
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado"
        )