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

        self.text = f"Bravo tu es {role} ! (garde le secret)."
        self.font_size = 10
        self.max_font_size = 100
        self.growth_speed = 0.5
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
        arcade.draw_text(
            text=self.text,       # On extrait la string de ton objet Text
            x=1920/2,            # Position X
            y=1080/2,            # Position Y
            color=arcade.color.WHITE,
            font_size=self.font_size,
            anchor_x="center",         # Arcade attend souvent "center" ou "left" ici
            anchor_y="center",
        )
        
        self.button_quit.draw()

    def on_update(self, delta_time: float):
        if self.font_size < self.max_font_size:
            self.font_size += self.growth_speed

