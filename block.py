import pyxel
from config import GRID_SIZE


class Block:
    def __init__(self, x, y, width, height, collide_with_player, collide_with_laser):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.collide_with_player = collide_with_player
        self.collide_with_laser = collide_with_laser
        if self.collide_with_laser == "ABSORB":
            self.absorb_side = ("TOP", "BOTTOM", "LEFT", "RIGHT")
        self.set_design()

    def set_design(self):
        if self.collide_with_laser == "ABSORB":
            self.color = 2
        elif self.collide_with_laser == "REFLECT":
            self.color = 7
        elif self.collide_with_laser == "TRANSPARENT":
            self.color = 12

    def update(self):
        pass

    def draw(self):
        if self.collide_with_player:
            pyxel.rect(self.x, self.y, self.width, self.height, self.color)
        else:
            pyxel.rectb(self.x, self.y, self.width, self.height, self.color)

    def check_collision(self, player):
        if not self.collide_with_player:
            return
        # プレイヤーとブロックの境界
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
            # 上からの衝突
            if player.y + GRID_SIZE - player.velocity_y <= self.y:
                player.y = self.y - GRID_SIZE
                player.velocity_y = 0
                player.on_ground = True

            # 下からの衝突
            elif player.y - player.velocity_y >= self.y + self.height:
                player.y = self.y + self.height
                player.velocity_y = max(player.velocity_y, 0)

            # 左からの衝突
            elif player.x + GRID_SIZE - player.velocity_x <= self.x:
                player.x = self.x - GRID_SIZE

            # 右からの衝突
            elif player.x - player.velocity_x <= block_right:
                player.x = block_right
            return (self.x, self.y)
