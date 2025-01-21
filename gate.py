import pyxel
from block import Block
from config import GRID_SIZE

class Gate(Block):
    def __init__(self, x, y, width, height, collidable_with_player, collide_with_laser, linked_absorbing_blocks):
        super().__init__(x, y, width, height, collidable_with_player, collide_with_laser)
        self.linked_absorbing_blocks = linked_absorbing_blocks
        self.does_exist = True
        self.height = GRID_SIZE

    def update(self):
        if any(block.absorbed for block in self.linked_absorbing_blocks):
            self.does_exist = False

    def draw(self):
        if self.does_exist:
            pyxel.rect(self.x, self.y, self.width, self.height, 14)
        else:
            self.draw_dashed_rect(self.x, self.y, self.width, self.height, 7)

    def check_collision(self, player):
        if self.does_exist:
            return super().check_collision(player)
        else:
            return False

    def draw_dashed_rect(self, x, y, width, height, color):
        width -= 1
        height -= 1
        dash_length = 2
        for i in range(0, width, dash_length * 2):
            pyxel.line(x + i, y, x + i + dash_length, y, color)  # 上辺
            pyxel.line(x + i + dash_length, y + height, min(x + width, x + i + dash_length * 2), y + height, color)  # 下辺
        for i in range(0, height, dash_length * 2):
            pyxel.line(x, y + i + dash_length, x, min(y + height, y + i + dash_length * 2), color)  # 左辺
            pyxel.line(x + width, y + i, x + width, y + i + dash_length, color)  # 右辺