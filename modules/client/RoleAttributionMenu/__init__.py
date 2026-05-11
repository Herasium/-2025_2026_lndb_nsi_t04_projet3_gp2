from modules.client.toolbox.entity import Entity
from modules.client.toolbox.text import Text
from typing import List
from modules.data import texture, data
from modules.client.mouse import mouse
from line_profiler import profile
import math
import arcade



class RoleAttribution(arcade.View):

    def __init__(self,role):

        super().__init__()
        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "RoleAttribution"
        self.role = role

        self.text = Text(x=1920/2,y=1080/2,width=500,height=100,text=f"You are a {role} ! (keep it a secret).")


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
        self.text.draw()

