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
        self.network_process = None
        self.run_connection = False
        multiprocessing.set_start_method('spawn', force=True)
        
    async def get_server_informations(self,ip,name):
        rx_queue = multiprocessing.Queue()
        tx_queue = multiprocessing.Queue()
        dead = multiprocessing.Value("i",0)
        
        message = json.dumps({"opcode":"server_info","data":{}})
        tx_queue.put(message)

        conn_obj = Connection(f"ws://{ip}:8765", rx_queue, tx_queue,dead)
        network_process = multiprocessing.Process(
            target=conn_obj.start, 
            daemon=True
        )
        network_process.start()

        loop = asyncio.get_running_loop()

        try:
            raw_msg: str = await loop.run_in_executor(
                None, rx_queue.get, True, 5.0
            )

        except queue.Empty:
            raw_msg = None

        dead.value = 1

        try:
            network_process.terminate()
            network_process.kill()
            network_process.join()
            network_process.close()
        except:
            pass
        
        if raw_msg is None:
            return {"nom":name,"nombre":0,"max":-1,"status":0}
        try:
           parsed = json.loads(raw_msg)
           parsed["nom"] = name
           return parsed
        except json.JSONDecodeError:
            return {"nom":name,"nombre":0,"max":-1,"status":0}

    def cut(self):
        if not self.network_process is None:
            self.dead_connection.value = 1
            self.network_process.terminate()
            self.network_process.kill()
            self.network_process.join()
            self.network_process.close()
            self.network_process = None
            self.run_connection = False

    def connect(self,ip):
        if self.run_connection:
            return 
        self.run_connection = True
        self.rx_queue = multiprocessing.Queue()
        self.tx_queue = multiprocessing.Queue()
        self.dead_connection = multiprocessing.Value("i",0)
        self.network_process = multiprocessing.Process(
                target=run_connection_worker, 
                args=(f"ws://{ip}:8765", self.rx_queue, self.tx_queue, self.dead_connection),
                daemon=True
            )
        self.network_process.start()


    def display(self, view: arcade.View) -> None:
        self.window.show_view(view)

    @profile
    def run(self):
        arcade.run()

def run_connection_worker(ip,rx,tx,dead):
    conn_obj = Connection(ip,rx,tx,dead)
    conn_obj.start()