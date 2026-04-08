import asyncio
import websockets

clients = set()

async def envoyer(websocket):
    while True:
        await websocket.send(await asyncio.to_thread(input))
    
async def recevoir(websocket):
    try:
        async for message in websocket:
            print(message)
    except websockets.ConnectionClosed:
        print("Serveur déconnecté")

async def main():
    async with websockets.connect("ws://localhost:8765") as websocket:
        await asyncio.gather(envoyer(websocket),recevoir(websocket))
asyncio.run(main())