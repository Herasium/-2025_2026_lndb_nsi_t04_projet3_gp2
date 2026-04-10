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

    client = Client()

    data.client = client


    client.display(MainMenu())
    client.run()

if __name__ == '__main__':
    main()