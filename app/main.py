import os
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter # Add this import

from .database import create_db_and_tables
from .routers import messages
from .routers import websocket # Add websocket
from .schemas import ErrorResponse, ErrorDetail
from .dependencies import rate_limit_dependency  # Add this import

# En una app de producción, esto se manejaría con Alembic o un script de inicialización
create_db_and_tables()

app = FastAPI(
    title="Chat Message API",
    description="Una API para procesar y recuperar mensajes de chat.",
    version="1.0.0",
)

@app.on_event("startup")
async def startup():
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis = Redis(host=redis_host, port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)

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
app.include_router(websocket.router)

@app.on_event("shutdown")
async def shutdown():
    await FastAPILimiter.close()

@app.get("/")
async def read_root(request: Request, rate_limiter: RateLimiter = Depends(rate_limit_dependency)):
    return {"message": "Bienvenido a la API de Mensajes de Chat"}