import pyxel

class Loader:

    def __init__(self):
        pass

    def load_images(self):
        pyxel.Image.load(0, 0, "assets/homescreen/homescreen_v1.png", include_colors=False)

    def load(self):
