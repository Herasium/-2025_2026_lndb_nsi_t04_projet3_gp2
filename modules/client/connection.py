import asyncio
from websockets.asyncio.client import connect
import multiprocessing
import queue
from modules.logger import Logger
import os

logger = Logger("Connection")

class Connection:
    def __init__(self, url, rx_queue, tx_queue, dead):
        self.url = url
        self.rx_queue = rx_queue
        self.tx_queue = tx_queue
        self.dead = dead

    async def recv_loop(self, websocket):
        try:
            async for msg in websocket:
                self.rx_queue.put(msg)
        except Exception:
            self.dead.value = 1
            logger.error("Dead Connection.")
            raise Exception("Dead")

    async def send_loop(self, websocket):
        try:
            while True:
                to_send = await asyncio.to_thread(self.tx_queue.get)
                await websocket.send(to_send)
        except Exception:
            self.dead.value = 1
            logger.error("Dead Connection.")
            raise Exception("Dead")


    async def run_async(self):
        async with connect(self.url) as websocket:
            recv_task = asyncio.create_task(self.recv_loop(websocket))
            send_task = asyncio.create_task(self.send_loop(websocket))

            done, pending = await asyncio.wait(
                (recv_task, send_task), return_when=asyncio.FIRST_EXCEPTION
            )

            for t in pending:
                t.cancel()
                with contextlib.suppress(Exception):
                    await t

    def start(self):
        logger.success(f"Connection process started. {self.url}")
        logger.success(f"Name: {__name__} Parent: {os.getppid()} Self: {os.getpid()}")
        asyncio.run(self.run_async())
