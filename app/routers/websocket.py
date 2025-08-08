from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/messages")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Los WebSockets pueden recibir mensajes, pero para este caso
            # solo nos interesa enviar actualizaciones, así que esperamos
            # un mensaje para mantener la conexión abierta.
            data = await websocket.receive_text()
            # Opcional: podrías procesar 'data' si los clientes envían mensajes
    except WebSocketDisconnect:
        manager.disconnect(websocket)
