from modules.client.connection import Connection
import threading
import arcade
import multiprocessing
from line_profiler import profile
from modules.data import data
import json
import queue
import asyncio

class Client:
    def __init__(self):
        self.current_view = None
        self.window: arcade.Window = arcade.Window(
            1920,
            1080,
            "Where Wolf?",
            fullscreen=True,
            update_rate=1 / 60,
            draw_rate=1 / 60,
        )

        data.client = self
        
    async def get_server_informations(self,ip,name):
        rx_queue = multiprocessing.Queue()
        tx_queue = multiprocessing.Queue()
        
        message = json.dumps({"opcode":"server_info","data":{}})
        tx_queue.put(message)

        self.conn_obj = Connection(f"ws://{ip}:8765", rx_queue, tx_queue)
        self.network_process = multiprocessing.Process(
            target=self.conn_obj.start, 
            daemon=True
        )
        self.network_process.start()

        loop = asyncio.get_running_loop()

        try:
            raw_msg: str = await loop.run_in_executor(
                None, rx_queue.get, True, 5.0
            )

        except queue.Empty:
            raw_msg = None

        if self.network_process.is_alive():
            self.network_process.terminate()
            self.network_process.join()

        if raw_msg is None:
            return {"nom":name,"nombre":0,"max":-1,"status":0}
        try:
           parsed = json.loads(raw_msg)
           parsed["nom"] = name
           return parsed
        except json.JSONDecodeError:
            return {"nom":name,"nombre":0,"max":-1,"status":0}


    def display(self, view: arcade.View) -> None:
        self.window.show_view(view)

    @profile
    def run(self):
        arcade.run()

        