from block import Block
import pyxel
from config import GRID_SIZE


class SavePoint(Block):
    def __init__(self, index_x, index_y, x, y):
        self.index_x = index_x
        self.index_y = index_y
        self.x = x
        self.y = y
        self.collide_with_laser = "TRANSPARENT"
        self.width = GRID_SIZE
        self.height = GRID_SIZE

    def draw(self, offset_x=0, offset_y=0):
        pyxel.rectb(
            self.x + offset_x, self.y + offset_y, GRID_SIZE, GRID_SIZE, 4
        )  # 保存ポイントを描画

    def check_collision(self, player):
        player_right = player.x + GRID_SIZE
        player_bottom = player.y + GRID_SIZE
        block_right = self.x + GRID_SIZE
        block_bottom = self.y + GRID_SIZE

        # 衝突しているか確認
        if (
            player.x < block_right
            and player_right > self.x
            and player.y < block_bottom
            and player_bottom > self.y
        ):
            player.save(self.index_x, self.index_y, self.x, self.y)
