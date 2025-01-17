import pyxel
from block import Block
from config import GRID_SIZE

class DeathBlock(Block):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def draw(self):
        # デス・ブロックの色を設定
        block_color = 8  # 赤
        pyxel.rect(self.x, self.y, self.width, self.height, block_color)

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
            and player_bottom > self.y
        ):
            # プレイヤーを初期位置に戻す
            player.x = GRID_SIZE
            player.y = pyxel.height - GRID_SIZE * 2
            player.velocity_y = 0
            player.on_ground = True 