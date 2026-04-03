import threading

from modules.client import Client
from modules.client.MainMenu import MainMenu
from modules.client.GameMenu import GameMenu
from modules.server import Server
from modules.data.loader import Loader

loader = Loader()
loader.load()

server = Server()
client = Client()

threading.Thread(target=server.run).start()
client.display(MainMenu())
client.run()