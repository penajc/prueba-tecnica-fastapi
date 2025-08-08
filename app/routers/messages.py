from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from .. import schemas, services
from ..dependencies import get_db, get_api_key, rate_limit_dependency  # Add rate_limit_dependency import
from app.routers.websocket import manager # Import the WebSocket manager

router = APIRouter(
    prefix="/api/messages",
    tags=["messages"],
    dependencies=[Depends(get_api_key)],
    responses={
        401: {"description": "Clave de API inválida o faltante"},
        422: {"model": schemas.ErrorResponse}
    },
)

@router.post(
    "/", 
    response_model=schemas.MessageResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_dependency)]  # This is already present and correct
)
async def create_message_endpoint(
    message: schemas.MessageCreate, db: Session = Depends(get_db)
):
    """Recibe, procesa y almacena un nuevo mensaje."""
    db_message = services.process_and_create_message(db=db, message=message)

    # Construye el objeto de respuesta con la estructura anidada correcta
    response_data = schemas.Message(
        message_id=db_message.message_id,
        session_id=db_message.session_id,
        content=db_message.content,
        timestamp=db_message.timestamp,
        sender=db_message.sender,
        metadata=schemas.MessageMetadata(
            word_count=db_message.word_count,
            character_count=db_message.character_count,
            processed_at=db_message.processed_at,
        ),
    )
    
    # Transmitir el nuevo mensaje a todos los clientes WebSocket conectados
    await manager.broadcast(response_data.model_dump_json())

    return schemas.MessageResponse(data=response_data)

@router.get("/search", response_model=schemas.MessagesResponse)
def search_messages_endpoint(
    query: str = Query(..., min_length=1, description="Texto a buscar en el contenido de los mensajes"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Busca mensajes por contenido, con paginación."""
    db_messages = services.search_messages(
        db=db, query_text=query, skip=skip, limit=limit
    )

    response_data = [
        schemas.Message(
            message_id=msg.message_id,
            session_id=msg.session_id,
            content=msg.content,
            timestamp=msg.timestamp,
            sender=msg.sender,
            metadata=schemas.MessageMetadata(
                word_count=msg.word_count,
                character_count=msg.character_count,
                processed_at=msg.processed_at,
            ),
        )
        for msg in db_messages
    ]

    return schemas.MessagesResponse(data=response_data)

@router.get("/{session_id}", response_model=schemas.MessagesResponse)
def read_messages_endpoint(
    session_id: str,
    sender: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Recupera mensajes para una sesión, con paginación y filtro."""
    db_messages = services.get_messages(
        db=db, session_id=session_id, sender=sender, skip=skip, limit=limit
    )
    
    # Mapear cada objeto de la BD a un esquema de respuesta
    response_data = [
        schemas.Message(
            message_id=msg.message_id,
            session_id=msg.session_id,
            content=msg.content,
            timestamp=msg.timestamp,
            sender=msg.sender,
            metadata=schemas.MessageMetadata(
                word_count=msg.word_count,
                character_count=msg.character_count,
                processed_at=msg.processed_at,
            ),
        )
        for msg in db_messages
    ]
    
    return schemas.MessagesResponse(data=response_data)