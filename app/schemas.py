from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal, Any, Generic, TypeVar

T = TypeVar("T")

# Estructura para respuestas de error estandarizadas
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: str | None = None

class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    error: ErrorDetail

# Estructura genérica para respuestas exitosas
class SuccessResponse(BaseModel, Generic[T]):
    status: Literal["success"] = "success"
    data: T

# Esquemas de Mensajes
class MessageBase(BaseModel):
    message_id: str
    session_id: str
    content: str
    timestamp: datetime
    # Valida que sender solo pueda ser 'user' o 'system'
    sender: Literal["user", "system"]

class MessageCreate(MessageBase):
    pass

class MessageMetadata(BaseModel):
    word_count: int
    character_count: int
    # Nuevo campo requerido por la prueba
    processed_at: datetime = Field(default_factory=datetime.utcnow)

class Message(MessageBase):
    metadata: MessageMetadata
    model_config = ConfigDict(from_attributes=True)

# Tipo específico para la respuesta de un solo mensaje
MessageResponse = SuccessResponse[Message]

# Tipo específico para la respuesta de una lista de mensajes
MessagesResponse = SuccessResponse[list[Message]]
