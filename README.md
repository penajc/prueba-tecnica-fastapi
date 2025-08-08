# API de Procesamiento de Mensajes de Chat

Esta es una API RESTful simple construida con FastAPI para procesar y recuperar mensajes de chat, como parte de una evaluación técnica para un desarrollador backend de Python.

## Características Principales

- **Autenticación por API Key**: Endpoints protegidos que requieren una clave en la cabecera `X-API-Key`.
- **Creación de Mensajes**: Endpoint para recibir, validar, procesar y almacenar mensajes.
- **Recuperación de Mensajes**: Endpoint para obtener mensajes por sesión, con paginación y filtrado.
- **Búsqueda de Mensajes**: Permite buscar mensajes por contenido de texto.
- **Validación de Datos**: Uso de Pydantic para una validación robusta de los datos de entrada.
- **Procesamiento Simple**: Filtrado de palabras inapropiadas y adición de metadatos (conteo de palabras, caracteres).
- **Manejo de Errores**: Respuestas de error estandarizadas y claras (HTTP 422 para validación).
- **Pruebas Completas**: Cobertura de pruebas superior al 99% para asegurar la robustez del código.
- **Arquitectura Limpia**: Código organizado siguiendo principios de separación de responsabilidades (routers, services, crud, schemas, models, dependencies).

## Puntos Extra Implementados

Además de los requisitos funcionales, se han implementado los siguientes puntos extra para mejorar la robustez, escalabilidad y experiencia de usuario:

- **Soporte Docker**: La aplicación está contenedorizada para asegurar un entorno de ejecución consistente y portable.
- **Limitación de Tasa (Rate Limiting)**: Implementado con `fastapi-limiter` y Redis para proteger la API contra abusos, limitando el número de solicitudes por usuario/IP.
- **WebSockets**: Un endpoint WebSocket (`/ws/messages`) permite la transmisión en tiempo real de nuevos mensajes a todos los clientes conectados.
- **Infraestructura como Código (IaC) con Kubernetes**: Se proporcionan manifiestos de Kubernetes para un despliegue escalable y portable de la aplicación y Redis en cualquier clúster de Kubernetes (probado con Minikube).

## Stack Tecnológico

- **Python 3.11+**
- **FastAPI**: Framework web de alto rendimiento para construir la API.
- **SQLAlchemy**: ORM para la interacción con la base de datos.
- **SQLite**: Base de datos para simplicidad en el desarrollo y pruebas.
- **Pydantic**: Para la validación y serialización de datos.
- **Pytest**: Para las pruebas automatizadas.
- **fastapi-limiter**: Para la implementación de la limitación de tasa.
- **Redis**: Base de datos en memoria utilizada por `fastapi-limiter`.
- **Docker**: Para la contenedorización de la aplicación.
- **Kubernetes (Minikube)**: Para la orquestación y despliegue local de contenedores.

---

## Configuración del Proyecto

1.  **Clonar el repositorio** (si aún no lo has hecho):
    ```bash
    git clone https://github.com/penajc/prueba-tecnica-fastapi.git
    cd prueba-tecnica-fastapi
    ```

2.  **Crear y activar un entorno virtual** (recomendado):
    ```bash
    python3 -m venv venv
    source venv/bin/activate # En macOS/Linux
    # venv\Scripts\activate # En Windows
    ```

3.  **Instalar las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

---

## Cómo Ejecutar la Aplicación

La forma recomendada de ejecutar la aplicación es usando Docker Compose, que levantará tanto la API como el servidor Redis necesario para la limitación de tasa.

1.  **Asegúrate de tener Docker instalado y en ejecución.**
2.  **Detén cualquier servidor Redis local** que pueda estar usando el puerto 6379 (ej. `sudo systemctl stop redis-server`).
3.  **Construye y levanta los servicios** con Docker Compose desde la raíz del proyecto:
    ```bash
    docker compose up --build
    ```
    La API estará disponible en `http://localhost:8000`.
    También puedes acceder a la documentación interactiva de Swagger UI en `http://localhost:8000/docs`.

---

## Documentación de la API

### Autenticación

Todos los endpoints de `/api/messages` requieren autenticación mediante una clave de API.
Debes incluir la cabecera `X-API-Key` en todas tus peticiones.

Para este proyecto, la clave es: `my-super-secret-key`

> **Nota**: En un entorno de producción, esta clave debería cargarse de forma segura a través de variables de entorno o un servicio de gestión de secretos.

### 1. Crear un Mensaje (POST)

- **Endpoint**: `POST /api/messages/`
- **Descripción**: Crea, procesa y almacena un nuevo mensaje. Este endpoint tiene **limitación de tasa** (5 solicitudes por minuto por IP) y **transmite el mensaje a los clientes WebSocket**.
- **Ejemplo con `curl`**:
    ```bash
    curl -X POST "http://localhost:8000/api/messages/"
         -H "Content-Type: application/json"
         -H "X-API-Key: my-super-secret-key"
         -d 
         {
           "message_id": "msg-12345",
           "session_id": "session-abcde",
           "content": "Hola, este es un mensaje de prueba.",
           "timestamp": "2023-10-27T10:00:00Z",
           "sender": "user"
         }
    ```

### 2. Recuperar Mensajes de una Sesión (GET)

- **Endpoint**: `GET /api/messages/{session_id}`
- **Descripción**: Obtiene todos los mensajes de una sesión específica. Soporta paginación y filtrado por remitente.
- **Ejemplo con `curl`**:
    ```bash
    # Obtener todos los mensajes de la sesión 'session-abcde'
    curl -X GET "http://127.0.0.1:8000/api/messages/session-abcde"
         -H "X-API-Key: my-super-secret-key"

    # Obtener solo los mensajes del usuario y con paginación
    curl -X GET "http://127.0.0.1:8000/api/messages/session-abcde?sender=user&skip=0&limit=10"
         -H "X-API-Key: my-super-secret-key"
    ```

### 3. Buscar Mensajes por Contenido (GET)

- **Endpoint**: `GET /api/messages/search`
- **Descripción**: Busca mensajes por contenido de texto, con paginación.
- **Parámetros de Consulta**:
    - `query` (obligatorio): El texto a buscar en el contenido de los mensajes.
    - `skip` (opcional, default `0`): Número de mensajes a saltar (para paginación).
    - `limit` (opcional, default `100`): Número máximo de mensajes a devolver.
- **Ejemplo con `curl`**:
    ```bash
    # Buscar mensajes que contengan la palabra "hola"
    curl -X GET "http://127.0.0.1:8000/api/messages/search?query=hola"
         -H "X-API-Key: my-super-secret-key"

    # Buscar mensajes que contengan "prueba" y paginar
    curl -X GET "http://127.0.0.1:8000/api/messages/search?query=prueba&limit=5&skip=0"
         -H "X-API-Key: my-super-secret-key"
    ```

### 4. Conexión WebSocket

- **Endpoint**: `ws://localhost:8000/ws/messages`
- **Descripción**: Permite a los clientes conectarse para recibir actualizaciones en tiempo real de nuevos mensajes creados.
- **Nota**: Este endpoint no aparece en la documentación de Swagger UI (`/docs`) debido a limitaciones de la especificación OpenAPI para WebSockets.
- **Cómo probar (con Python)**:
    1.  Asegúrate de tener `websockets` instalado (`pip install websockets`).
    2.  Crea un archivo `test_websocket.py` con el siguiente contenido:
        ```python
        import asyncio
        import websockets
        import json

        async def test_websocket_client():
            uri = "ws://localhost:8000/ws/messages"
            print(f"Conectando a {uri}...")
            async with websockets.connect(uri) as websocket:
                print("Conexión establecida. Esperando mensajes...")
                try:
                    while True:
                        message = await websocket.recv()
                        print(f"Mensaje recibido: {message}")
                except websockets.exceptions.ConnectionClosedOK:
                    print("Conexión cerrada normalmente.")
                except Exception as e:
                    print(f"Error en el WebSocket: {e}")

        if __name__ == "__main__":
            asyncio.run(test_websocket_client())
        ```
    3.  Ejecuta el script: `python3 test_websocket.py`
    4.  En otra terminal, envía un mensaje POST a `/api/messages/`. Deberías ver el JSON del mensaje en la terminal del script.

---

## Despliegue con Kubernetes (Minikube)

Para probar la aplicación en un entorno Kubernetes local, puedes usar Minikube.

1.  **Instalar Minikube y kubectl**: Sigue las instrucciones oficiales de Minikube y kubectl.
    - Minikube: `https://minikube.sigs.k8s.io/docs/start/`
    - kubectl: `https://kubernetes.io/docs/tasks/tools/install-kubectl/`

2.  **Iniciar Minikube**:
    ```bash
    minikube start
    ```

3.  **Configurar el entorno Docker de Minikube**: Esto permite que `docker build` construya imágenes directamente en el demonio Docker de Minikube.
    ```bash
    eval $(minikube docker-env)
    ```
    *(Ejecuta esto en cada nueva terminal donde vayas a construir imágenes para Minikube).*

4.  **Construir la imagen Docker de la aplicación**: 
    Desde la raíz del proyecto, construye la imagen:
    ```bash
    docker build -t fastapi-chat-api:latest .
    ```

5.  **Desplegar los manifiestos de Kubernetes**: 
    Aplica los archivos YAML en el directorio `k8s/` a tu clúster de Minikube:
    ```bash
    minikube kubectl -- apply -f k8s/
    ```

6.  **Verificar el estado de los Pods**: 
    Asegúrate de que los pods estén en estado `Running`:
    ```bash
    minikube kubectl -- get pods
    ```

7.  **Obtener la URL de la aplicación**: 
    Minikube te proporcionará la URL para acceder a tu API:
    ```bash
    minikube service fastapi-app-service --url
    ```
    Usa esta URL para probar la API (ej. `http://192.168.49.2:31086/docs`).

**Limpieza de Minikube**:
Cuando termines de probar, puedes detener y eliminar el clúster de Minikube:
```bash
minikube stop
minikube delete
```

---

## Cómo Ejecutar las Pruebas

Para ejecutar el conjunto de pruebas y ver el informe de cobertura, asegúrate de tener el entorno virtual activado y ejecuta:

```bash

# Ejecutar pruebas y mostrar cobertura en la terminal
pytest --cov=app --cov-report=term-missing
```