import pyxel
from modules.client.connection import Connection
from modules.client.view import View
import threading

class Client:
    def __init__(self):
        self.current_view = None
        self.connection = Connection()
        pyxel.init(160, 120)

    def update(self):
        self.current_view.update()

    def draw(self):
        self.current_view.draw()

    def run(self):
        print(1)
        threading.Thread(target=self.connection.run).start()
        print(2)
        pyxel.run(self.update, self.draw)