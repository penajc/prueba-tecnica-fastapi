# API de Procesamiento de Mensajes de Chat

Esta es una API RESTful simple construida con FastAPI para procesar y recuperar mensajes de chat, como parte de una evaluación técnica para un desarrollador backend de Python.

## Características

- **Autenticación por API Key**: Endpoints protegidos que requieren una clave en la cabecera `X-API-Key`.
- **Creación de Mensajes**: Endpoint para recibir, validar, procesar y almacenar mensajes.
- **Recuperación de Mensajes**: Endpoint para obtener mensajes por sesión, con paginación y filtrado.
- **Validación de Datos**: Uso de Pydantic para una validación robusta de los datos de entrada.
- **Procesamiento Simple**: Filtrado de palabras inapropiadas y adición de metadatos.
- **Manejo de Errores**: Respuestas de error estandarizadas y claras.
- **Pruebas Completas**: Cobertura de pruebas superior al 95%.
- **Arquitectura Limpia**: Código organizado siguiendo principios de separación de responsabilidades.

## Stack Tecnológico

- **Python 3.10+**
- **FastAPI**: Framework web de alto rendimiento.
- **SQLAlchemy**: ORM para la interacción con la base de datos.
- **SQLite**: Base de datos para simplicidad.
- **Pydantic**: Para la validación de datos.
- **Pytest**: Para las pruebas automatizadas.

---

## Configuración del Proyecto

1.  **Clonar el repositorio (si aplica)**:
    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-directorio>
    ```

2.  **Crear y activar un entorno virtual**:
    ```bash
    # En Windows
    python -m venv venv
    venv\Scripts\activate

    # En macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

---

## Cómo Ejecutar la Aplicación

Para iniciar el servidor de desarrollo, ejecuta el siguiente comando desde el directorio raíz del proyecto:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

También puedes acceder a la documentación interactiva de Swagger UI en `http://127.0.0.1:8000/docs`.

---

## Documentación de la API

### Autenticación

Todos los endpoints de `/api/messages` requieren autenticación mediante una clave de API.
Debes incluir la cabecera `X-API-Key` en todas tus peticiones.

Para este proyecto, la clave es: `my-super-secret-key`

> **Nota**: En un entorno de producción, esta clave debería cargarse de forma segura a través de variables de entorno o un servicio de gestión de secretos.

### 1. Crear un Mensaje

- **Endpoint**: `POST /api/messages/`
- **Descripción**: Crea, procesa y almacena un nuevo mensaje.
- **Ejemplo con `curl`**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/messages/" \
         -H "Content-Type: application/json" \
         -H "X-API-Key: my-super-secret-key" \
         -d '{
           "message_id": "msg-12345",
           "session_id": "session-abcde",
           "content": "Hola, este es un mensaje de prueba.",
           "timestamp": "2023-10-27T10:00:00Z",
           "sender": "user"
         }'
    ```

### 2. Recuperar Mensajes de una Sesión

- **Endpoint**: `GET /api/messages/{session_id}`
- **Descripción**: Obtiene todos los mensajes de una sesión específica.
- **Ejemplo con `curl`**:
    ```bash
    # Obtener todos los mensajes de la sesión 'session-abcde'
    curl -X GET "http://127.0.0.1:8000/api/messages/session-abcde" \
         -H "X-API-Key: my-super-secret-key"

    # Obtener solo los mensajes del usuario y con paginación
    curl -X GET "http://127.0.0.1:8000/api/messages/session-abcde?sender=user&skip=0&limit=10" \
         -H "X-API-Key: my-super-secret-key"
    ```

### 3. Buscar Mensajes por Contenido

- **Endpoint**: `GET /api/messages/search`
- **Descripción**: Busca mensajes por contenido de texto, con paginación.
- **Parámetros de Consulta**:
    - `query` (obligatorio): El texto a buscar en el contenido de los mensajes.
    - `skip` (opcional, default `0`): Número de mensajes a saltar (para paginación).
    - `limit` (opcional, default `100`): Número máximo de mensajes a devolver.
- **Ejemplo con `curl`**:
    ```bash
    # Buscar mensajes que contengan la palabra "hola"
    curl -X GET "http://127.0.0.1:8000/api/messages/search?query=hola" \
         -H "X-API-Key: my-super-secret-key"

    # Buscar mensajes que contengan "prueba" y paginar
    curl -X GET "http://127.0.0.1:8000/api/messages/search?query=prueba&limit=5&skip=0" \
         -H "X-API-Key: my-super-secret-key"
    ```

---

## Cómo Ejecutar las Pruebas

Para ejecutar el conjunto de pruebas y ver el informe de cobertura, asegúrate de tener el entorno virtual activado y ejecuta:

```bash
# Ejecutar pruebas y mostrar cobertura en la terminal
pytest --cov=app --cov-report=term-missing
```
```
