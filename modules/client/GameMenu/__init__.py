from modules.client.toolbox.entity import Entity
from modules.data import texture
from modules.client.mouse import mouse
from line_profiler import profile
import arcade

class GameMenu(arcade.View):

    def __init__(self):
        super().__init__()
        self.background_color: arcade.color = arcade.color.BLACK
        self.name = "GameMenu"
        self.bg = Entity(0,0,1920,1080,texture.get("main_background"))
        self.x = 0

    @profile
    def on_mouse_motion(
        self, x: float, y: float, delta_x: float, delta_y: float
    ) -> None:
        mouse.position = (x, y)


    
    @profile
    def on_mouse_press(self,x,y,buttons,modifier):
        pass

    @profile
    def on_mouse_release(self,x,y,buttons,modifier):
        if self.button_quit.touched :
            self.button_quit.sprite = texture.get("create_default")
            arcade.exit()

    def on_draw(self):
        self.clear()
        self.bg.draw()

    @profile
    def on_update(self,delta_time):
        self.x = (self.x + 1) % 150
