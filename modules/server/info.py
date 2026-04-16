
import json

async def server_informations(message,websocket):
    raw = {"nom":"Serveur Distant","nombre":0,"max":10,"status":2}
    await websocket.send(json.dumps(raw))
