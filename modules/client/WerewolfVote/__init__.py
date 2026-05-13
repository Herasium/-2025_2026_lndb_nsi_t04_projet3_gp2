from modules.client.toolbox.entity import Entity
from modules.client.toolbox.text import Text
from typing import List
from modules.data import texture, data
from modules.client.mouse import mouse
from line_profiler import profile
import math
import arcade



class WerewolfVote(arcade.View):

    def __init__(self,choices,back):

        super().__init__()
        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "WerewolfVote"
        self.button_quit = Entity(1820, 990, 64, 64,texture.get("quit_default"))
        self.bg = Entity(0,0,1920,1080,texture.get("join_background"))
        self.text = Text(x=1920/2,y=1080/2,width=500,height=100,text=f"It's WEREWOLF time !")
        self.back = back

        self.choices = choices
        self.buttons = [] 
        offset = 0
        for i in choices:
            self.buttons.append(Text(x=1920/2 + offset,y=1080/2-200,width=100,height=100,text=f"{i["name"]}"))
            offset += 200

    @profile
    def on_mouse_motion(
        self, x: float, y: float, delta_x: float, delta_y: float
    ) -> None:
        mouse.position = (x, y)
        pass

    @profile
    def on_mouse_press(self,x,y,buttons,modifier):
        c = 0
        for i in self.buttons:
            if i.touched:
                self.back(self.choices[c])

            c += 1
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
        self.button_quit.draw()
        for i in self.buttons:
            i.draw()

