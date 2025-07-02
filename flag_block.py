import pyxel
from block import Block
from config import GRID_SIZE


class FlagBlock(Block):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        absorb_side="TOP",
        collide_with_player=True,
        collide_with_laser=False,
    ):
        super().__init__(x, y, width, height, collide_with_player, collide_with_laser)
        self.absorb_side = absorb_side
        self.absorbed = 0

    def draw(self, offset_x=0, offset_y=0):
        # 吸収面に応じたアクセント色を設定
        if self.absorb_side == "TOP":
            pyxel.blt(self.x + offset_x, self.y + offset_y, 1, 0, 16, -16, -16, 0)
        elif self.absorb_side == "BOTTOM":
            pyxel.blt(self.x + offset_x, self.y + offset_y, 1, 0, 16, 16, 16, 0)
        elif self.absorb_side == "LEFT":
            pyxel.blt(self.x + offset_x, self.y + offset_y, 1, 16, 16, -16, -16, 0)
        elif self.absorb_side == "RIGHT":
            pyxel.blt(self.x + offset_x, self.y + offset_y, 1, 16, 16, 16, 16, 0)
