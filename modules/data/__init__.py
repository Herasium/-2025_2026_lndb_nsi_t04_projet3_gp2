
from modules.data.id_generator import random_id

class Texture:

    def __init__(self):
        self.textures = {"__default__": None}

    def add(self,name,texture):
        self.textures[name] = texture
    
    def get(self,name):
        if name in self.textures:
            return self.textures[name]
        return self.textures["__default__"]


class Data:
    def __init__(self):
        self.LOGGER_MIN = 0
        self.VERSION = 0

data = Data()
texture = Texture()