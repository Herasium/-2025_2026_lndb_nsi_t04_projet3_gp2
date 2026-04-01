import asyncio
from websockets.asyncio.client import connect


class Connection():
    def __init__(self,url="ws://localhost:8765"):
        self.connection = None
        self.url = url

    async def connect(self):
        async with connect(self.url) as websocket:
            self.connection = websocket
            await websocket.send("Hello world!")
            message = await websocket.recv()
            print(message)

    def run(self):
        asyncio.run(self.connect())