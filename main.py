import threading

from modules.client import Client
from modules.client.MainMenu import MainMenu

from modules.server import Server
from modules.data.loader import Loader

<<<<<<< HEAD
=======
import multiprocessing
from modules.data import data
from line_profiler import profile

@profile
>>>>>>> 6737dafa641a80ed08716b79954b8a788630bee5
def main():
    loader = Loader()
    loader.load()

    client = Client()

<<<<<<< HEAD
=======
    data.client = client

    server_process = multiprocessing.Process(
            target=server.run, 
            daemon=True
    )

    server_process.start()
>>>>>>> 6737dafa641a80ed08716b79954b8a788630bee5
    client.display(MainMenu())
    client.run()

if __name__ == '__main__':
    main()