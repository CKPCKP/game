import pyxel
from config import GRID_SIZE

class CanBeLaserPotion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False

    def draw(self, offset_x=0, offset_y=0):
        draw_x = self.x + offset_x
        draw_y = self.y + offset_y
        if not self.collected:
            # レーザーポーションの見た目（例：赤い四角＋白い線）
            pyxel.rect(draw_x, draw_y, GRID_SIZE, GRID_SIZE, 8)  # 赤い四角
            pyxel.line(draw_x, draw_y, draw_x + GRID_SIZE - 1, draw_y + GRID_SIZE - 1, 7)  # 白い斜線
