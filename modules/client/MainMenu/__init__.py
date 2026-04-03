
from modules.client.toolbox.entity import Entity
from modules.data import texture


import arcade

class MainMenu(arcade.View):

    def __init__(self):
        super().__init__()
        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "MainMenu"
        self.bg = Entity(0,0,1920,1080,texture.get("main_background"))
        self.cube = Entity(0,0,100,100)
        self.x = 0

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.cube.draw()

    def on_update(self,delta_time):
        self.x = (self.x + 1) % 150
        self.cube.x = self.x