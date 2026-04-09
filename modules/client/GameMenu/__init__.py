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
        self.data = [{"nom":"Serveur 1","nombre":10,"max":15,"status":"En Cours."},{"nom":"Serveur 2","nombre":1,"max":100,"status":"En Attente."},{"nom":"Serveur 3","nombre":0,"max":2,"status":"Hors Ligne."}]
        self.button_quit = Entity(1820, 1000, 64, 64,texture.get("create_default"))

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
        self.button_quit.draw()
        arcade.draw_lbwh_rectangle_outline(100,200,500,300, arcade.color.RED)

    @profile
    def on_update(self,delta_time):
        self.x = (self.x + 1) % 150
