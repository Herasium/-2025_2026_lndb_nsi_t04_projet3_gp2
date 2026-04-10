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
        self.cadre = Entity(320,220,256*5,128*5,texture.get("server_bg"))
        self.x = 0

        self.button_quit = Entity(1820, 990, 64, 64,texture.get("quit_default"))


    def setup_texts(self) -> None:

        self.data: List[str] = [
            {"nom":"Serveur 1","nombre":10,"max":15,"status":"En Cours."},
            {"nom":"Serveur 2","nombre":1,"max":100,"status":"En Attente."},
            {"nom":"Serveur 3","nombre":0,"max":2,"status":"Hors Ligne."},
            {"nom":"Serveur 4","nombre":2,"max":19,"status":"Hors Ligne."}
        ]

        self.server: List[Text] = []
        self.case_server: List[Entity] = []

        a = (256*3.5) + 10
        for i in self.data :
            a = a - 36*5
            self.server.append(
                Text(
                    x=640,
                    y=a + self.camera,
                    text=f"Nouveau {i["nom"]} pour {i["nombre"]} personnes",
                    align=("left", "center"),
                    size=25,
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

        ZONE_X_MIN, ZONE_X_MAX = 300, 300 + (256 * 5)
        ZONE_Y_MIN, ZONE_Y_MAX = 220, 220 + (128 * 5)

        for case in self.case_server:
            if ZONE_X_MIN <= case.x <= ZONE_X_MAX and ZONE_Y_MIN <= case.y <= ZONE_Y_MAX:
                case.draw()

        for text in self.server:
            if ZONE_X_MIN <= text.x <= ZONE_X_MAX and ZONE_Y_MIN <= text.y <= ZONE_Y_MAX:
                text.draw()


        # for n in self.case_server:
        #     n.draw()

        # for i in self.server:
        #     i.draw()
        
    @profile
    def on_update(self,delta_time):
        self.x = (self.x + 1) % 150

    def on_mouse_scroll(
        self, x: float, y: float, scroll_x: float, scroll_y: float
    ) -> None:
        """Met à jour le décalage vertical de la caméra et reconstruit la mise en page."""
        ZONE_X_MIN, ZONE_X_MAX = 320, 320 + (256 * 5)
        ZONE_Y_MIN, ZONE_Y_MAX = 220, 220 + (128 * 5)
        
        if ZONE_X_MIN <= x <= ZONE_X_MAX and ZONE_Y_MIN <= y <= ZONE_Y_MAX:
            self.camera += scroll_y * -data.MOUSE_SENSI
            self.camera = max(self.camera, 0)
            self.camera = min(self.camera, data.MAX_SCROLL)
            self.setup_texts()
        else:
            pass
