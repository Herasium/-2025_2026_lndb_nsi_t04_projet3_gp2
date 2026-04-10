import arcade

from modules.data import data,texture

class Loader:

    def __init__(self):
        pass

    def load_images(self):
        texture.add("main_background",arcade.Sprite("assets/homescreen/homescreen_v1.png"))
        texture.add("join_default",arcade.Sprite("assets/buttons/join_default.png"))
        texture.add("join_click",arcade.Sprite("assets/buttons/join_click.png"))
        texture.add("join_hover",arcade.Sprite("assets/buttons/join_hover.png"))
        texture.add("settings_click",arcade.Sprite("assets/icons/settings_click.png"))
        texture.add("settings_default",arcade.Sprite("assets/icons/settings_default.png"))
        texture.add("quit_click",arcade.Sprite("assets/icons/quit_click.png"))
        texture.add("quit_default",arcade.Sprite("assets/icons/quit_default.png"))
        texture.add("server_bg",arcade.Sprite("assets/server_join/server_bg.png"))
        texture.add("server_case",arcade.Sprite("assets/server_join/server_case.png"))

    def load(self):
        self.load_images()
        self.load_font()


    def load_font(self):
        arcade.load_font("assets/fonts/press_start.ttf")