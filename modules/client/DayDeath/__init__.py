from modules.client.toolbox.entity import Entity
from modules.client.toolbox.text import Text
from typing import List
from modules.data import texture, data
from modules.client.mouse import mouse
from line_profiler import profile
import math
import arcade



class DayDeath(arcade.View):

    def __init__(self,death):

        super().__init__()
        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "DayDeath"
        self.death = death

        self.bg = Entity(0,0,1920,1080,texture.get("join_background"))
        self.texts = []

        offset = 0

        for i in self.death:
            self.texts.append(Text(x=1920/2,y=1080/2+offset,width=500,height=100,text=f"{i["name"]} has died. They were a {i["role"]}."))
            offset += 100


    @profile
    def on_mouse_motion(
        self, x: float, y: float, delta_x: float, delta_y: float
    ) -> None:
        mouse.position = (x, y)
        pass

    @profile
    def on_mouse_press(self,x,y,buttons,modifier):
        pass

    @profile
    def on_mouse_release(self,x,y,buttons,modifier):
        pass

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.texts.draw()

