from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .database import create_db_and_tables
from .routers import messages
from .schemas import ErrorResponse, ErrorDetail

# En una app de producción, esto se manejaría con Alembic o un script de inicialización
create_db_and_tables()

app = FastAPI(
    title="Chat Message API",
    description="Una API para procesar y recuperar mensajes de chat.",
    version="1.0.0",
)

# Manejador de errores de validación personalizado
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extraemos el primer error para dar un mensaje más claro
    first_error = exc.errors()[0]
    field = ".".join(str(loc) for loc in first_error["loc"][1:])
    message = first_error["msg"]
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INVALID_FORMAT",
                message=f"Error de validación en el campo '{field}'",
                details=message,
            )
        ).model_dump(),
    )

app.include_router(messages.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Mensajes de Chat"}
