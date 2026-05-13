from modules.client.toolbox.entity import Entity
from modules.client.toolbox.text import Text
from typing import List
from modules.data import texture, data
from modules.client.mouse import mouse
from line_profiler import profile
import math
import arcade



class WerewolfNight(arcade.View):

    def __init__(self):

        super().__init__()
        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "WerewolfNight"

        self.bg = Entity(0,0,1920,1080,texture.get("join_background"))
        self.text = Text(x=1920/2,y=1080/2,width=500,height=100,text=f"It's WEREWOLF time !")
        self.button_quit = Entity(1820, 990, 64, 64,texture.get("quit_default"))


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
        self.text.draw()
        self.bg.draw()
        self.button_quit.draw()
