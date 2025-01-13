import pyxel
from player import Player


class Block:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def update(self):
        pass

    def draw(self):
        pyxel.rect(self.x, self.y, self.width, self.height, 11)

    def check_collision(self, player):
        # プレイヤーとブロックの境界
        player_right = player.x + 8
        player_bottom = player.y + 8
        block_right = self.x + self.width
        block_bottom = self.y + self.height

        # 衝突しているか確認
        if (
            player.x < block_right
            and player_right > self.x
            and player.y < block_bottom
            and player_bottom > self.y
        ):
            # 上からの衝突
            if player.y + 8 - player.velocity_y <= self.y:
                player.y = self.y - 8
                player.velocity_y = 0
                player.on_ground = True  # プレイヤーがブロックの上にいる場合

            # 下からの衝突
            elif player.y - player.velocity_y >= self.y + self.height:
                player.y = self.y + self.height
                player.velocity_y = max(player.velocity_y, 0)  # 下方向の速度を止める

            # 左からの衝突
            elif player.x + 8 - player.velocity_x <= self.x:
                player.x = self.x - 8

            # 右からの衝突
            elif player.x - player.velocity_x <= block_right:
                player.x = block_right 