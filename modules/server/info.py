
import json

async def server_informations(message,client):
    raw = {"nom":"Serveur Distant","nombre":0,"max":10,"status":2}
    await client.conn.send(json.dumps(raw))
