# gaming bitches
import multiprocessing
from modules.data import data
import json
import pyglet
import asyncio

from modules.logger import Logger

from modules.client.WaitingMenu import WaitingMenu
from modules.client.RoleAttributionMenu import RoleAttribution
from modules.client.NightMenu import NightMenu
from modules.client.WerewolfNight import WerewolfNight
from modules.client.WerewolfVote import WerewolfVote
from modules.client.WerewolfEnd import WerewolfEnd
from modules.client.DayMenu import DayMenu
from modules.client.KilledMenu import KilledMenu
from modules.client.NightDeath import NightDeath
from modules.client.DayDeath import DayDeath
from modules.client.DayVote import DayVote

logger = Logger("Orchestrator")

class Orchestator:

    def __init__(self,ip):
        self.ip = ip

    async def send(self,opcode,data = {}):
        message = json.dumps({"opcode":opcode,"data":data})
        self.tx.put_nowait(message)

    async def waiting_room_update(self,received):
        def switch_view(dt):
            new_menu = WaitingMenu(received["players"], received["status"])
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)

    async def player_role(self,received):
        def switch_view(dt):
            new_menu = RoleAttribution(received["role"])
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)

    async def switch_night(self):
        def switch_view(dt):
            new_menu = NightMenu()
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)

    async def night_werewolf_start(self):
        def switch_view(dt):
            new_menu = WerewolfNight()
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)

    async def night_werewolf_end(self):
        def switch_view(dt):
            new_menu = WerewolfEnd()
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)

    async def switch_day(self):
        def switch_view(dt):
            new_menu = DayMenu()
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)

    async def night_death(self,received):
        def switch_view(dt):
            new_menu = NightDeath(received["death"])
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)

    async def killed(self):
        def switch_view(dt):
            new_menu = KilledMenu()
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)        

    async def night_death(self,received):
        def switch_view(dt):
            new_menu = DayDeath(received["death"])
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)      

    async def night_werewolf_vote(self,received):

        def back(choice):
            asyncio.run(self.send("night_werewolf_vote_response",{"vote":choice["id"]}))
            

        def switch_view(dt):
            new_menu = WerewolfVote(received["villagers"],back)
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)

    async def day_vote(self,received):

        def back(choice):
            asyncio.run(self.send("day_vote_response",{"vote":choice["id"]}))
            
        def switch_view(dt):
            new_menu = DayVote(received["villagers"],back)
            data.client.display(new_menu)

        pyglet.clock.schedule_once(switch_view, 0)

    async def read(self):


        raw = self.rx.get()

        parsed = json.loads(raw)

        logger.debug(f"{parsed}")

        opcode = parsed["opcode"]
        data = parsed["data"]

        match opcode:
            case "waiting_room_list_update":
                await self.waiting_room_update(data)
            case "player_role":
                await self.player_role(data)
            case "switch_night":
                await self.switch_night()
            case "night_werewolf_start":
                await self.night_werewolf_start()
            case "night_werewolf_vote":
                await self.night_werewolf_vote(data)
            case "switch_day":
                await self.switch_day()
            case "night_werewolf_end":
                await self.night_werewolf_end()
            case "killed":
                await self.killed()
            case "night_death":
                await self.night_death(data)
            case "day_death":
                await self.night_death(data)
            case "day_vote":
                await self.day_vote(data)

    async def run(self):
        data.client.connect(self.ip)

        self.rx: multiprocessing.Queue = data.client.rx_queue
        self.tx: multiprocessing.Queue = data.client.tx_queue

        await self.send("player_join",{"name":data.nickname})

        while True:
            await self.read()