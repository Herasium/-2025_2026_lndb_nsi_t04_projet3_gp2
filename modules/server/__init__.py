import asyncio
from websockets.asyncio.server import serve

from modules.server.client import Client
from modules.data import random_id
from modules.logger import Logger

logger: Logger = Logger("ServerCore")

class Server():

    def __init__(self):
        self.clients = {}

    async def receive(self, websocket):
        id = random_id()
        new_client = Client(websocket, id)
        self.clients[id] = new_client
        logger.debug(f"New connected client {id}")

        try:
            async for message in websocket:
                await self.handle_message(message) 
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            logger.debug(f"Disconnected client {id}")
            del self.clients[id]

    async def serve(self):
        async with serve(self.receive, "0.0.0.0", 8765) as server:
            await server.serve_forever()

    def run(self):
        asyncio.run(self.serve())