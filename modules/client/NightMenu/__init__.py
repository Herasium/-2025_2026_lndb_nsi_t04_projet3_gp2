from modules.client.toolbox.entity import Entity
from modules.client.toolbox.text import Text
from typing import List
from modules.data import texture, data
from modules.client.mouse import mouse
from line_profiler import profile
import math
import arcade



class NightMenu(arcade.View):

    def __init__(self):

        super().__init__()
        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "NightMenu"
        self.button_quit = Entity(1820, 990, 64, 64,texture.get("quit_default"))
        self.bg = Entity(0,0,1920,1080,texture.get("join_background"))
        self.houses_bg = Entity(0,0,1920,1080,texture.get("houses_background"))
        self.sky_bg = Entity(0,0,1920,1080,texture.get("night_sky"))
        self.moon_bg = Entity(0,-1000,1920,1080,texture.get("big_moon"))
        self.text = f"Le village s'endort !!"
        self.moon_rise_speed = 170
        self.font_size = 1
        self.max_font_size = 18
        self.growth_speed = 0.55


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
        # self.bg.draw()
        self.sky_bg.draw()
        self.moon_bg.draw()
        self.houses_bg.draw()

        self.button_quit.draw()
        arcade.draw_text(
            text=self.text,
            x=1920/2, 
            y=740,
            color=(0,0,0),
            font_size=self.font_size,
            font_name="Press Start 2P",
            anchor_x="center",
            anchor_y="center",
        )
        
    
    def on_update(self, delta_time: float):
        if self.font_size < self.max_font_size:
            self.font_size += self.growth_speed
        
        if self.moon_bg.y < 0:
            self.moon_bg.y += self.moon_rise_speed * delta_time
            self.moon_bg.y = min(self.moon_bg.y, 0)