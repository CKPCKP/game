import pyxel
from config import GRID_SIZE

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False

    def draw(self, offset_x=0, offset_y=0):
        if not self.collected:
            pyxel.circ(self.x + offset_x + GRID_SIZE // 2, self.y + offset_y + GRID_SIZE // 2, GRID_SIZE // 4, 10)  # コインを描画