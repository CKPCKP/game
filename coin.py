import pyxel
from config import GRID_SIZE

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False

    def draw(self):
        if not self.collected:
            pyxel.circ(self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, GRID_SIZE // 4, 10)  # コインを描画