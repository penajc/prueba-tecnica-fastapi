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
