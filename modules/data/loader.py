import pyxel

from modules.data import data,texture

class Loader:

    def __init__(self):
        pass

    def load_images(self):
        img = pyxel.Image(192,108)
        img.load(0, 0, "assets/homescreen/homescreen_v1.png", include_colors=True)
        texture.add("main_background",img)
        print(texture.textures)

    def load(self):
        self.load_images()