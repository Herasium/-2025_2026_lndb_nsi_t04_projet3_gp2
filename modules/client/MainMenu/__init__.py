
from modules.client.toolbox.entity import Entity
from modules.data import texture
from modules.client.mouse import mouse
from line_profiler import profile
import arcade

class MainMenu(arcade.View):

    def __init__(self):
        super().__init__()
        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "MainMenu"
        self.bg = Entity(0,0,1920,1080,texture.get("main_background"))
        self.button_join = Entity(100,200,400,100,texture.get("join_default"))
        self.button_setting = Entity(1750,1000,32,32,texture.get("create_default"))
        self.button_quit = Entity(1820, 1000, 64, 64,texture.get("create_default"))
        self.x = 0

    @profile
    def on_mouse_motion(
        self, x: float, y: float, delta_x: float, delta_y: float
    ) -> None:
        mouse.position = (x, y)
        if self.button_join.touched:
            self.button_join.sprite = texture.get("join_hover")
        else:
            self.button_join.sprite = texture.get("join_default")

        if self.button_setting.touched:
            self.button_setting.sprite = texture.get("create_hover")
        else:
            self.button_setting.sprite = texture.get("create_default")

        if self.button_quit.touched:
            self.button_quit.sprite = texture.get("create_hover")
        else:
            self.button_quit.sprite = texture.get("create_default")

    
    @profile
    def on_mouse_press(self,x,y,buttons,modifier):
        if self.button_join.touched :
            self.button_join.sprite = texture.get("join_click")

        if self.button_setting.touched :
            self.button_setting.sprite = texture.get("create_click")

        if self.button_quit.touched :
            self.button_quit.sprite = texture.get("create_click")


    @profile
    def on_mouse_release(self,x,y,buttons,modifier):
        if self.button_join.touched :
            self.button_join.sprite = texture.get("join_default")

        if self.button_setting.touched :
            self.button_setting.sprite = texture.get("create_default")

        if self.button_quit.touched :
            self.button_quit.sprite = texture.get("create_default")

    def on_draw(self):
        self.clear()
        self.bg.draw()
        self.button_join.draw()
        self.button_setting.draw()
        self.button_quit.draw()

    @profile
    def on_update(self,delta_time):
        self.x = (self.x + 1) % 150
