import arcade

from modules.data import data,texture

class Loader:

    def __init__(self):
        pass

    def load_images(self):
        
        # Font
        texture.add("main_background",arcade.Sprite("assets/homescreen/homescreen_v1.png"))
        texture.add("join_background",arcade.Sprite("assets/join_background/server_screen.png"))

        # MainMenu
        texture.add("join_default",arcade.Sprite("assets/buttons/join_default.png"))
        texture.add("join_click",arcade.Sprite("assets/buttons/join_click.png"))
        texture.add("join_hover",arcade.Sprite("assets/buttons/join_hover.png"))

        texture.add("nickname",arcade.Sprite("assets/buttons/Nickname_Button.png"))
        texture.add("nickname_typing",arcade.Sprite("assets/buttons/Nickname_Button_Typing.png"))

        texture.add("settings_click",arcade.Sprite("assets/icons/settings_click.png"))
        texture.add("settings_default",arcade.Sprite("assets/icons/settings_default.png"))

        texture.add("quit_click",arcade.Sprite("assets/icons/quit_click.png"))
        texture.add("quit_default",arcade.Sprite("assets/icons/quit_default.png"))

        texture.add("server_bg",arcade.Sprite("assets/server_join/server_bg.png"))
        texture.add("server_case_default",arcade.Sprite("assets/server_join/server_case_default.png"))
        texture.add("server_case_hover",arcade.Sprite("assets/server_join/server_case_hover.png"))

        texture.add("server_online",arcade.Sprite("assets/status/status_0.png"))
        texture.add("server_waiting",arcade.Sprite("assets/status/status_1.png"))
        texture.add("server_offline",arcade.Sprite("assets/status/status_2.png"))

        texture.add("add_default",arcade.Sprite("assets/buttons/add_default.png"))
        texture.add("add_click",arcade.Sprite("assets/buttons/add_click.png"))
        texture.add("add_hover",arcade.Sprite("assets/buttons/add_hover.png"))

    def load(self):
        self.load_images()
        self.load_font()


    def load_font(self):
        arcade.load_font("assets/fonts/press_start.ttf")