from modules.client.toolbox.entity import Entity
from modules.client.toolbox.text import Text
from typing import List
from modules.data import texture, data
from modules.client.mouse import mouse
from line_profiler import profile
import math
import arcade



class WaitingMenu(arcade.View):

    def __init__(self):
        super().__init__()
        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "WaitingMenu"
        # self.bg = Entity(0,0,1920,1080,texture.get("main_background"))
        self.button_quit = Entity(1820, 990, 64, 64,texture.get("quit_default"))
        self.x = 0

        # self.table_ronde = arcade.draw_circle_filled(960, 540, 60, [109, 155, 195, 255])

        self.data: List[str] = [
            {"nom": "Marine", "statue": "en ligne"},
            {"nom": "Eudocie", "statue": "en ligne"},
            {"nom": "Louise", "statue": "deco"},
            {"nom": "Elisa", "statue": "deco"},
            {"nom": "Jeanne", "statue": "deco"},
        ]
        
        self.nb_perso = 0
        self.perso: List[str] = []

        for n in self.data:
            if n["statue"] == "en ligne":
                self.nb_perso += 1

        a = 0
        for i in self.data:
            if i["statue"] == "en ligne":
                a = 2*(math.pi) // self.nb_perso
                self.perso.append(
                    Text(
                        x=260*(math.cos(a))+960,
                        y=260*(math.sin(a))+540,
                        text=f"{i["nom"]}",
                        align=("right", "top"),
                        size=12,
                    )
                )
        
        print (self.nb_perso, self.perso)



    @profile
    def on_mouse_motion(
        self, x: float, y: float, delta_x: float, delta_y: float
    ) -> None:
        mouse.position = (x, y)
        pass

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
        # self.bg.draw()
        self.button_quit.draw()
        arcade.draw_circle_filled(960, 540, 260, [109, 155, 195, 255])

        for p in self.perso:
            p.draw()

    @profile
    def on_update(self,delta_time):
        self.x = (self.x + 1) % 150
