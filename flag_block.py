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
        # ブロックの共通色
        block_color = 9
        accent_color = 7

        # ブロックを描画
        pyxel.rect(self.x + offset_x, self.y + offset_y, self.width, self.height, block_color)

        # 吸収面に応じたアクセント色を設定
        if self.absorb_side == "TOP":
            pyxel.line(self.x + offset_x, self.y + offset_y, self.x + offset_x + self.width - 1, self.y + offset_y, accent_color)
        elif self.absorb_side == "BOTTOM":
            pyxel.line(
                self.x + offset_x,
                self.y + offset_y + self.height,
                self.x + offset_x + self.width - 1,
                self.y + offset_y + self.height,
                accent_color,
            )
        elif self.absorb_side == "LEFT":
            pyxel.line(self.x + offset_x, self.y + offset_y, self.x + offset_x, self.y + offset_y + self.height - 1, accent_color)
        elif self.absorb_side == "RIGHT":
            pyxel.line(
                self.x + offset_x + self.width - 1,
                self.y + offset_y,
                self.x + offset_x + self.width - 1,
                self.y + offset_y + self.height - 1,
                accent_color,
            )
