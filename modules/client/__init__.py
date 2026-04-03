import pyxel
from modules.client.connection import Connection
from modules.client.view import View
import threading

class Client:
    def __init__(self):
        self.current_view = None
        self.connection = Connection()
        pyxel.init(192, 108)

    def update(self):
        self.current_view.update()

    def draw(self):
        self.current_view.draw()

    def run(self):

        threading.Thread(target=self.connection.run).start()
        pyxel.run(self.update, self.draw)