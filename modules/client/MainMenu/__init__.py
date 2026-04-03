from modules.client import View
from modules.data import texture

import pyxel

class MainMenu(View):

    def __init__(self):
        super().__init__()
        self.name = "MainMenu"
        self.x = 0

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(0,0,texture.get("main_background"),0,0,192,108)
        pyxel.rect(self.x, 0, 8, 8, 9)

    def update(self):
        self.x = (self.x + 1) % 150