import pyxel

from modules.data import data,texture

class Loader:

    def __init__(self):
        pass

    def load_images(self):
        img = pyxel.Image.load(0, 0, "assets/homescreen/homescreen_v1.png", include_colors=False)
        texture.add("img","main_background")

    def load(self):
