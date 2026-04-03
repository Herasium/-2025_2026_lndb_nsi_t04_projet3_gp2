from modules.client.connection import Connection
import threading
import arcade

class Client:
    def __init__(self):
        self.current_view = None
        self.connection = Connection()
        self.window: arcade.Window = arcade.Window(
            1920,
            1080,
            "Where Wolf?",
            fullscreen=True,
            update_rate=1 / 60,
            draw_rate=1 / 60,
        )

    def display(self, view: arcade.View) -> None:
        self.window.show_view(view)

    def run(self):

        threading.Thread(target=self.connection.run).start()
        arcade.run()