import asyncio
from websockets.asyncio.client import connect
import multiprocessing
import contextlib
import queue
import os
import time



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
        except Exception as e:
            self.dead.value = 1
            print(f"dead, {e}")
            raise Exception("Dead")

    async def send_loop(self, websocket):
        try:
            while True:
                try:
                    to_send = self.tx_queue.get_nowait()
                    await websocket.send(to_send)
                except queue.Empty:
                    await asyncio.sleep(0.05)
        except Exception as e:
            self.dead.value = 1
            print(f"dead, {e}")
            raise Exception("Dead")


    async def run_async(self):
        async with connect(self.url) as websocket:
            recv_task = asyncio.create_task(self.recv_loop(websocket))
            send_task = asyncio.create_task(self.send_loop(websocket))

            done, pending = await asyncio.wait(
                (recv_task, send_task), return_when=asyncio.FIRST_EXCEPTION
            )

            for t in pending:
                print(f"Canceled  {time.time()}")
                t.cancel()
                with contextlib.suppress(Exception):
                    await t

    def start(self):
        print(self.url)
        asyncio.run(self.run_async())
