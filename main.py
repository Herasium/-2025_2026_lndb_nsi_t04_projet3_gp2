import pyxel

pyxel.init(192, 108)

def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(0)
    pyxel.rect(10, 10, 1, 1, 11)

pyxel.run(update, draw)