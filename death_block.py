import pyxel
from block import Block
from config import GRID_SIZE


class DeathBlock(Block):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        start_position,
        collide_with_player=True,
        collide_with_laser=False,
    ):
        super().__init__(x, y, width, height, collide_with_player, collide_with_laser)
        self.start_position = start_position

    def draw(self, offset_x=0, offset_y=0):
        pyxel.blt(self.x + offset_x, self.y + offset_y, 1, 48 + self.frame_index * GRID_SIZE, 0, 16, 16, 0)

    def check_collision(self, player):
        # プレイヤーとデス・ブロックの境界
        player_right = player.x + GRID_SIZE
        player_bottom = player.y + GRID_SIZE
        block_right = self.x + self.width
        block_bottom = self.y + self.height

        # 衝突しているか確認
        if (
            player.x < block_right
            and player_right > self.x
            and player.y < block_bottom
            and player_bottom >= self.y
        ):
            player.alive = False
