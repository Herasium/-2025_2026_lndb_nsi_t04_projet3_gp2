from modules.client.toolbox.entity import Entity
from typing import List
from modules.client.toolbox.text import Text
import asyncio
from modules.data import texture
from modules.client.mouse import mouse
from line_profiler import profile
from modules.data import data
import arcade

class GameMenu(arcade.View):

    def __init__(self):
        super().__init__()

        self.camera = 0

        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "GameMenu"

        self.data: List[str] = [
            {"nom":"Serveur 1","nombre":10,"max":15,"status":1},
            {"nom":"Serveur 2","nombre":1,"max":100,"status":1},
            {"nom":"Serveur 3","nombre":0,"max":2,"status":1},
            {"nom":"Serveur 4","nombre":2,"max":19,"status":1}
        ]

        #1: En Cours
        #0: Hors Ligne
        #2: En Ligne

        self.setup_texts()

        self.bg = Entity(0,0,1920,1080,texture.get("main_background"))
        self.cadre = Entity(320,220,256*5,128*5,texture.get("server_bg"))
        self.x = 0
        self._fetch_task = asyncio.run_coroutine_threadsafe(
            self._fetch_and_update(),
            data.loop,
        )
        self.button_quit = Entity(1820, 990, 64, 64,texture.get("quit_default"))

    async def _fetch_and_update(self) -> None:
        try:
            new_data = await data.client.get_server_informations("192.168.2.155")
        except Exception as exc:
            return
        self.data[0] = new_data      
        self.setup_texts()           


    def setup_texts(self) -> None:

        self.server: List[Text] = []
        self.case_server: List[Entity] = []

        a = (256*3.5) +5
        for i in self.data :
            a = a - 36*5
            self.server.append(
                Text(
                    x=960,
                    y=a + self.camera,
                    text=f"{i["nom"]}  {i["nombre"]}/{i["max"]} ({i["status"]})",
                    align=("center", "center"),
                    size=18,
                )
            )
        b = (256*3)+42
        for i in self.data:
            b = b - 36*5
            self.case_server.append(
                Entity(
                    x=320,
                    y=b + self.camera,
                    width=256*5,
                    height=36*5,
                    sprite=texture.get("server_case"),
                )
            )

    @profile
    def on_mouse_motion(
        self, x: float, y: float, delta_x: float, delta_y: float
    ) -> None:
        mouse.position = (x, y)

    @profile
    def on_mouse_press(self,x,y,buttons,modifier):
        if self.button_quit.touched :
            self.button_quit.sprite = texture.get("quit_click")

    @profile
    def on_mouse_release(self,x,y,buttons,modifier):
        if self.button_quit.touched :
            self.button_quit.sprite = texture.get("quit_default")
            arcade.exit()

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.cadre.draw()
        self.button_quit.draw()

        for n in self.case_server:
            n.draw()

        for i in self.server:
            i.draw()
        
    @profile
    def on_update(self,delta_time):
        self.x = (self.x + 1) % 150

    def on_mouse_scroll(
        self, x: float, y: float, scroll_x: float, scroll_y: float
    ) -> None:
        """Met à jour le décalage vertical de la caméra et reconstruit la mise en page."""
        
        self.camera += scroll_y * -data.MOUSE_SENSI
        self.camera = max(self.camera, 0)
        self.camera = min(self.camera, data.MAX_SCROLL)
        self.setup_texts()

