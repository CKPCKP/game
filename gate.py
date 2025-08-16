import pyxel
from block import Block
from config import GRID_SIZE


class Gate(Block):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        collidable_with_player,
        collide_with_laser,
        initial_exist=True,
    ):
        super().__init__(
            x, y, width, height, collidable_with_player, collide_with_laser
        )
        self.does_exist = initial_exist
        self.initial_exist = initial_exist
        self.height = GRID_SIZE

    def update(self, gate_toggle = False):
        self.does_exist = self.initial_exist ^ gate_toggle
        if self.does_exist:
            self.collide_with_laser = "ABSORB"
            self.collide_with_player = True
        else:
            self.collide_with_laser = "TRANSPARENT"
            self.collide_with_player = False
        super().update()

    def draw(self, offset_x=0, offset_y=0):
        v = 3 if self.initial_exist else 4
        if self.does_exist:
            pyxel.blt(
                self.x + offset_x, self.y + offset_y, 1, 0 + self.frame_index * GRID_SIZE, v * GRID_SIZE, 16, 16, 0
            )
            # pyxel.rect(self.x + offset_x, self.y + offset_y, self.width, self.height, 14)
        else:
            pyxel.blt(
                self.x + offset_x, self.y + offset_y, 1, 16 + self.frame_index * GRID_SIZE, v * GRID_SIZE, 16, 16, 0
            )

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
            pyxel.line(
                x + i + dash_length,
                y + height,
                min(x + width, x + i + dash_length * 2),
                y + height,
                color,
            )  # 下辺
        for i in range(0, height, dash_length * 2):
            pyxel.line(
                x,
                y + i + dash_length,
                x,
                min(y + height, y + i + dash_length * 2),
                color,
            )  # 左辺
            pyxel.line(x + width, y + i, x + width, y + i + dash_length, color)  # 右辺
