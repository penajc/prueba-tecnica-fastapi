from sqlalchemy.orm import Session
from . import models, schemas

def create_message(db: Session, message: schemas.MessageCreate, metadata: schemas.MessageMetadata):
    db_message = models.Message(
        message_id=message.message_id,
        session_id=message.session_id,
        content=message.content,
        timestamp=message.timestamp,
        sender=message.sender,
        word_count=metadata.word_count,
        character_count=metadata.character_count,
        processed_at=metadata.processed_at
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_by_session(db: Session, session_id: str, sender: str | None, skip: int = 0, limit: int = 100):
    query = db.query(models.Message).filter(models.Message.session_id == session_id)
    
    if sender:
        query = query.filter(models.Message.sender == sender)
        
    return query.offset(skip).limit(limit).all()
