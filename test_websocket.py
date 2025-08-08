import asyncio
import websockets
import json
     
async def test_websocket():
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
    asyncio.run(test_websocket())
