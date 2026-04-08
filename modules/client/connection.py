import asyncio
from websockets.asyncio.client import connect
import multiprocessing
import queue

class Connection:
    def __init__(self, url, rx_queue, tx_queue):
        self.url = url
        self.rx_queue = rx_queue 
        self.tx_queue = tx_queue 

    async def run_async(self):
        async with connect(self.url) as websocket:
            while True:
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                    self.rx_queue.put(msg)
                except (asyncio.TimeoutError, Exception):
                    pass

                try:
                    to_send = self.tx_queue.get_nowait()
                    await websocket.send(to_send)
                except queue.Empty:
                    pass
                
                await asyncio.sleep(0.001)

    def start(self):
        asyncio.run(self.run_async())