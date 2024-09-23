from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str = Field(
        default=...,
        description="ID de la sesión"
    )

    input: str = Field(
        default=...,
        description="Mensaje del usuario"
    )

class ChatResponse(BaseModel):
    respuesta: str = Field(
        default=...,
        description="Mensaje de respuesta"
    )
    session_id: Optional[UUID] = Field(
        default=None,
        description="ID de la Sesión"
    )

class Language(BaseModel):
        language: str = Field(description="idioma del mensaje del usuario")
        translate: str = Field(description="traducción al español del mensaje del usuario")

class Name(BaseModel):
        user_name: str = Field(description="Nombre del usuario")