from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from .database import SessionLocal

# En una aplicación real, esta clave debería cargarse desde variables de entorno o un servicio de secretos.
API_KEY_SECRET = "my-super-secret-key"

api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_api_key(api_key_header: str = Depends(api_key_header_scheme)):
    """Dependencia que valida la clave de API en la cabecera."""
    if not api_key_header or api_key_header != API_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de API inválida o faltante",
        )
    return api_key_header
