from modules.client.connection import Connection
import threading
import arcade
import multiprocessing
from line_profiler import profile

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

        self.rx_queue = multiprocessing.Queue()
        self.tx_queue = multiprocessing.Queue()
        
        self.conn_obj = Connection("ws://192.168.2.177:8765", self.rx_queue, self.tx_queue)
        self.network_process = multiprocessing.Process(
            target=self.conn_obj.start, 
            daemon=True
        )
        

    def display(self, view: arcade.View) -> None:
        self.window.show_view(view)

    @profile
    def run(self):
        self.network_process.start()
        arcade.run()

        