import threading

from modules.client import Client
from modules.client.MainMenu import MainMenu
from modules.client.GameMenu import GameMenu
from modules.server import Server

server = Server()
client = Client()

threading.Thread(target=server.run).start()
client.current_view = MainMenu()
client.run()