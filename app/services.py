import re
from sqlalchemy.orm import Session
from datetime import datetime
from . import crud, schemas, models

# Lista simple de palabras prohibidas para el ejemplo
BANNED_WORDS = {"inapropiada", "prohibida", "baneada"}

def _filter_content(content: str) -> str:
    """Filtra palabras prohibidas del contenido (insensible a mayúsculas)."""
    for word in BANNED_WORDS:
        # Usamos re.sub con el flag re.IGNORECASE para reemplazar sin importar may/min
        content = re.sub(re.escape(word), "****", content, flags=re.IGNORECASE)
    return content

def process_and_create_message(db: Session, message: schemas.MessageCreate) -> models.Message:
    """Procesa y guarda un nuevo mensaje."""
    # 1. Filtrado de contenido
    filtered_content = _filter_content(message.content)
    message.content = filtered_content

    # 2. Cálculo de metadatos
    metadata = schemas.MessageMetadata(
        word_count=len(filtered_content.split()),
        character_count=len(filtered_content),
        processed_at=datetime.utcnow()
    )

    # 3. Llamada al CRUD para guardar en BD
    return crud.create_message(db=db, message=message, metadata=metadata)

def get_messages(
    db: Session, session_id: str, sender: str | None, skip: int, limit: int
) -> list[models.Message]:
    """Obtiene mensajes por sesión con formato estandarizado."""
    return crud.get_messages_by_session(
        db=db, session_id=session_id, sender=sender, skip=skip, limit=limit
    )

def search_messages(
    db: Session, query_text: str, skip: int = 0, limit: int = 100
) -> list[models.Message]:
    """Busca mensajes por contenido con paginación."""
    return crud.search_messages_by_content(
        db=db, query_text=query_text, skip=skip, limit=limit
    )
