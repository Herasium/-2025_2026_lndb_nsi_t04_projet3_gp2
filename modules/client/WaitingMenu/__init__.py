from modules.client.toolbox.entity import Entity
from typing import List
from modules.data import texture, data
from modules.client.mouse import mouse
from line_profiler import profile
import arcade



class WaitingMenu(arcade.View):

    def __init__(self):
        super().__init__()
        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "WaitingMenu"
        self.bg = Entity(0,0,1920,1080,texture.get("main_background"))
        self.button_quit = Entity(1820, 990, 64, 64,texture.get("quit_default"))
        self.x = 0

        self.data: List[str] = [
            {"nom": "Marine"},
            {"nom": "Eudocie"},
            {"nom": "Louise"},
            {"nom": "Elisa"},
            {"nom": "Jeanne"},
        ]

    @profile
    def on_mouse_motion(
        self, x: float, y: float, delta_x: float, delta_y: float
    ) -> None:
        mouse.position = (x, y)
        if self.button_join.touched:
            self.button_join.sprite = texture.get("join_hover")
        else:
            self.button_join.sprite = texture.get("join_default")


    
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
        self.button_quit.draw()

    @profile
    def on_update(self,delta_time):
        self.x = (self.x + 1) % 150
