from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .. import schemas, services
from ..dependencies import get_db

router = APIRouter(
    prefix="/api/messages",
    tags=["messages"],
    responses={422: {"model": schemas.ErrorResponse}},
)

@router.post(
    "/", 
    response_model=schemas.MessageResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_message_endpoint(
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
    
    return schemas.MessageResponse(data=response_data)

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
