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
            return None
        # プレイヤーとブロックの境界
        player_right = player.x + GRID_SIZE
        player_bottom = player.y + GRID_SIZE
        block_right = self.x + self.width
        block_bottom = self.y + self.height

        if (player.x < block_right and player_right > self.x and
            player.y < block_bottom and player_bottom > self.y):
            # x軸, y軸の重なり（オーバーラップ）の深さを計算
            overlap_x = min(player_right, block_right) - max(player.x, self.x)
            overlap_y = min(player_bottom, block_bottom) - max(player.y, self.y)

            if overlap_x < overlap_y:
                # 横方向の衝突
                player_center_x = player.x + GRID_SIZE / 2
                block_center_x = self.x + self.width / 2
                if player_center_x < block_center_x:
                    return ("LEFT", self)
                else:
                    return ("RIGHT", self)
            else:
                # 縦方向の衝突
                player_center_y = player.y + GRID_SIZE / 2
                block_center_y = self.y + self.height / 2
                if player_center_y < block_center_y:
                    return ("TOP", self)
                else:
                    return ("BOTTOM", self)
        return None