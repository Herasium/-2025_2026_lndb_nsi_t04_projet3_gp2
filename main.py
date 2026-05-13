import threading

from modules.client import Client
from modules.client.MainMenu import MainMenu
from modules.client.WaitingMenu import WaitingMenu
from modules.client.NightMenu import NightMenu
from modules.client.WerewolfVote import WerewolfVote
from modules.client.RoleAttributionMenu import RoleAttribution
from modules.client.WerewolfNight import WerewolfNight

from modules.server import Server
from modules.data.loader import Loader

import multiprocessing
from modules.data import data
from line_profiler import profile
import asyncio

def back (a):
    print(a)
@profile
def main():
    loader = Loader()
    loader.load()

    client = Client()

    data.client = client
    data.loop = start_async_loop()

    # client.display(WerewolfVote([{"name":"Eudoc", "id":"0001"}, {"name":"Marine", "id":"0002"}], back))
    client.display(NightMenu())
    #client.display(MainMenu)
    client.run()

def start_async_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True).start()
    return loop

if __name__ == '__main__':
    main()