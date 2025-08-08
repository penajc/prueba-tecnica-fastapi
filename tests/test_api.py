from fastapi.testclient import TestClient
from datetime import datetime

# Pruebas para el endpoint POST /api/messages
def test_create_message_success(client: TestClient):
    """Prueba la creación exitosa de un mensaje."""
    timestamp = datetime.utcnow().isoformat() + "Z"  # Formato ISO 8601
    response = client.post(
        "/api/messages/",
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
    assert data["data"]["message_id"] == "test-msg-1"
    assert data["data"]["metadata"]["word_count"] == 2

def test_create_message_invalid_sender(client: TestClient):
    """Prueba el error de validación para un sender inválido."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    response = client.post(
        "/api/messages/",
        json={
            "message_id": "test-msg-2",
            "session_id": "test-session-1",
            "content": "Contenido de prueba",
            "timestamp": timestamp,
            "sender": "invalid_sender",  # Sender no válido
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "INVALID_FORMAT"

# Pruebas para el endpoint GET /api/messages/{session_id}
def test_read_messages_by_session(client: TestClient):
    """Prueba la recuperación de mensajes por session_id."""
    # Crear dos mensajes en la misma sesión
    client.post("/api/messages/", json={"message_id": "msg1", "session_id": "s1", "content": "a", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})
    client.post("/api/messages/", json={"message_id": "msg2", "session_id": "s1", "content": "b", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "system"})
    # Crear un mensaje en otra sesión (no debe aparecer)
    client.post("/api/messages/", json={"message_id": "msg3", "session_id": "s2", "content": "c", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})

    response = client.get("/api/messages/s1")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) == 2

def test_read_messages_filter_by_sender(client: TestClient):
    """Prueba el filtrado por sender."""
    client.post("/api/messages/", json={"message_id": "msg4", "session_id": "s3", "content": "d", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})
    client.post("/api/messages/", json={"message_id": "msg5", "session_id": "s3", "content": "e", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "system"})

    response = client.get("/api/messages/s3?sender=user")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["sender"] == "user"

def test_read_messages_pagination(client: TestClient):
    """Prueba la paginación con limit y offset."""
    for i in range(5):
        client.post("/api/messages/", json={"message_id": f"msg-page-{i}", "session_id": "s4", "content": f"{i}", "timestamp": datetime.utcnow().isoformat() + "Z", "sender": "user"})

    # Pedir 2 mensajes saltando los primeros 2
    response = client.get("/api/messages/s4?limit=2&skip=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert data["data"][0]["message_id"] == "msg-page-2"
