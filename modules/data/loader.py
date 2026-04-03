import arcade

from modules.data import data,texture

class Loader:

    def __init__(self):
        pass

    def load_images(self):
        texture.add("main_background",arcade.Sprite("assets/homescreen/homescreen_v1.png"))

    def load(self):
        self.load_images()