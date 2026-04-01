import asyncio
from websockets.asyncio.server import serve

from modules.server.client import Client
from modules.data import random_id
from modules.logger import Logger

logger: Logger = Logger("ServerCore")

class Server():

    def __init__(self):
        self.clients = {}

    async def receive(self,websocket):
        id = random_id()
        new_client = Client(websocket,id)

        self.clients[id] = new_client

        logger.debug(f"New connected client {id}")

    async def serve(self):
        async with serve(self.receive, "localhost", 8765) as server:
            await server.serve_forever()

    def run(self):
        asyncio.run(self.serve())