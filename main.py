import threading

from modules.client import Client
from modules.client.MainMenu import MainMenu

from modules.server import Server
from modules.data.loader import Loader

import multiprocessing
from modules.data import data
from line_profiler import profile

@profile
def main():
    loader = Loader()
    loader.load()

    server = Server()
    client = Client()

    data.client = client

    server_process = multiprocessing.Process(
            target=server.run, 
            daemon=True
    )

    server_process.start()
    client.display(MainMenu())
    client.run()

if __name__ == '__main__':
    main()