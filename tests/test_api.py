from fastapi.testclient import TestClient
from datetime import datetime

# Clave de API válida para las pruebas
API_KEY = "my-super-secret-key"
HEADERS = {"X-API-Key": API_KEY}

# --- Pruebas de Autenticación ---

def test_create_message_no_api_key(client: TestClient):
    """Prueba que una petición sin clave de API es rechazada."""
    response = client.post("/api/messages/", json={})
    assert response.status_code == 401
    assert response.json() == {"detail": "Clave de API inválida o faltante"}

def test_create_message_wrong_api_key(client: TestClient):
    """Prueba que una petición con una clave de API incorrecta es rechazada."""
    response = client.post(
        "/api/messages/",
        headers={"X-API-Key": "wrong-key"},
        json={},
    )
    assert response.status_code == 401

# --- Pruebas para el endpoint POST /api/messages ---

def test_create_message_success(client: TestClient):
    """Prueba la creación exitosa de un mensaje."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    response = client.post(
        "/api/messages/",
        headers=HEADERS,
        json={
            "message_id": "test-msg-1",
            "session_id": "test-session-1",
            "content": "Hola mundo",
            "timestamp": timestamp,
            "sender": "user",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"

def test_create_message_invalid_sender(client: TestClient):
    """Prueba el error de validación para un sender inválido."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    response = client.post(
        "/api/messages/",
        headers=HEADERS,
        json={
            "message_id": "test-msg-2",
            "session_id": "test-session-1",
            "content": "Contenido de prueba",
            "timestamp": timestamp,
            "sender": "invalid_sender",
        },
    )
    assert response.status_code == 422

# --- Pruebas para el endpoint GET /api/messages/{session_id} ---

def test_read_messages_by_session(client: TestClient):
    """Prueba la recuperación de mensajes por session_id."""
    client.post("/api/messages/", headers=HEADERS, json={"message_id": "msg1", "session_id": "s1", "content": "a", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})
    client.post("/api/messages/", headers=HEADERS, json={"message_id": "msg2", "session_id": "s1", "content": "b", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "system"})
    client.post("/api/messages/", headers=HEADERS, json={"message_id": "msg3", "session_id": "s2", "content": "c", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})

    response = client.get("/api/messages/s1", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2

def test_read_messages_filter_by_sender(client: TestClient):
    """Prueba el filtrado por sender."""
    client.post("/api/messages/", headers=HEADERS, json={"message_id": "msg4", "session_id": "s3", "content": "d", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})
    client.post("/api/messages/", headers=HEADERS, json={"message_id": "msg5", "session_id": "s3", "content": "e", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "system"})

    response = client.get("/api/messages/s3?sender=user", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1

def test_read_messages_pagination(client: TestClient):
    """Prueba la paginación con limit y offset."""
    for i in range(5):
        client.post("/api/messages/", headers=HEADERS, json={"message_id": f"msg-page-{i}", "session_id": "s4", "content": f"{i}", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})

    response = client.get("/api/messages/s4?limit=2&skip=2", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2

# --- Pruebas para el endpoint GET /api/messages/search ---

def test_search_messages_by_content(client: TestClient):
    """Prueba la búsqueda de mensajes por contenido."""
    client.post("/api/messages/", headers=HEADERS, json={"message_id": "search-msg-1", "session_id": "s5", "content": "Hola mundo de la búsqueda", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})
    client.post("/api/messages/", headers=HEADERS, json={"message_id": "search-msg-2", "session_id": "s5", "content": "Otro mensaje para buscar", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "system"})
    client.post("/api/messages/", headers=HEADERS, json={"message_id": "search-msg-3", "session_id": "s6", "content": "Mundo feliz", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})

    response = client.get("/api/messages/search?query=mundo", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) == 2
    assert any("Hola mundo" in msg["content"] for msg in data["data"])
    assert any("Mundo feliz" in msg["content"] for msg in data["data"])

def test_search_messages_case_insensitive(client: TestClient):
    """Prueba que la búsqueda es insensible a mayúsculas y minúsculas."""
    client.post("/api/messages/", headers=HEADERS, json={"message_id": "search-msg-4", "session_id": "s7", "content": "Mensaje con PALABRA", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})

    response = client.get("/api/messages/search?query=palabra", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert "Mensaje con PALABRA" in data["data"][0]["content"]

def test_search_messages_no_results(client: TestClient):
    """Prueba que la búsqueda no devuelve resultados si no hay coincidencias."""
    response = client.get("/api/messages/search?query=nomatch", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) == 0

def test_validation_error_handler(client: TestClient):
    """Prueba que el manejador de errores de validación personalizado funciona."""
    response = client.post(
        "/api/messages/",
        headers=HEADERS,
        json={
            "message_id": "test-msg-invalid",
            "session_id": "test-session-invalid",
            "content": "Contenido de prueba",
            "timestamp": "invalid-timestamp", # Esto debería causar un error de validación
            "sender": "user",
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "INVALID_FORMAT"
    assert "Error de validación en el campo 'timestamp'" in data["error"]["message"]
    assert "Input should be a valid datetime or date, invalid character in year" in data["error"]["details"]
