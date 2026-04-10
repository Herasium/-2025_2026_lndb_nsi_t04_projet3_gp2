import threading

from modules.client import Client
from modules.client.MainMenu import MainMenu

from modules.server import Server
from modules.data.loader import Loader

def main():
    loader = Loader()
    loader.load()

    client = Client()

    client.display(MainMenu())
    client.run()

if __name__ == '__main__':
    main()