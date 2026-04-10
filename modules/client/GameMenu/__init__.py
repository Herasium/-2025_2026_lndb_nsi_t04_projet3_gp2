from modules.client.toolbox.entity import Entity
from typing import List
from modules.client.toolbox.text import Text
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

        self.setup_texts()

        self.bg = Entity(0,0,1920,1080,texture.get("main_background"))
        self.cadre = Entity(500,500,256*2,128*2,texture.get("server_bg"))
        self.x = 0

        self.button_quit = Entity(1820, 990, 64, 64,texture.get("quit_default"))


    def setup_texts(self) -> None:

        self.data: List[str] = [
            {"nom":"Serveur 1","nombre":10,"max":15,"status":"En Cours."},
            {"nom":"Serveur 2","nombre":1,"max":100,"status":"En Attente."},
            {"nom":"Serveur 3","nombre":0,"max":2,"status":"Hors Ligne."},
        ]

        self.server: List[Text] = []
        self.case_server: List[Entity] = []

        a = 560
        for i in self.data :
            a = a - 45
            self.server.append(
                Text(
                    x=160,
                    y=a + self.camera,
                    text=f"Nouveau {i["nom"]} pour {i["nombre"]} personnes",
                    align=("left", "center"),
                    size=16,
                )
            )

        for i in self.data:
            a = a - 45
            self.case_server.append(
                Entity(
                    x=160,
                    y=a + self.camera,
                    width=256,
                    height=36,
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
        # arcade.draw_lbwh_rectangle_outline(100,200,500,300, arcade.color.RED)

        for i in self.server:
            i.draw()
        
        for n in self.case_server:
            n.draw()

    @profile
    def on_update(self,delta_time):
        self.x = (self.x + 1) % 150

    def on_mouse_scroll(
        self, x: float, y: float, scroll_x: float, scroll_y: float
    ) -> None:
        """Met à jour le décalage vertical de la caméra et reconstruit la mise en page."""
        data.self.MAX_SCROLL = 256 * 2
        self.camera += scroll_y * -data.MOUSE_SENSI
        self.camera = max(self.camera, 0)
        self.camera = min(self.camera, data.self.MAX_SCROLL)
        self.setup_texts()
