import pyxel
from config import GRID_SIZE

class Player:
    def __init__(self, screen_height):
        self.x = GRID_SIZE
        self.y = screen_height - GRID_SIZE * 2
        self.velocity_x = 0
        self.velocity_y = 0
        self.lasers = []
        self.direction = "RIGHT"
        self.on_ground = False

    def update(self, player_speed, jump_strength, gravity, max_gravity):
        # 横の移動
        if pyxel.btn(pyxel.KEY_LEFT):
            self.velocity_x = -player_speed
            self.x -= player_speed
            self.direction = "LEFT"
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.velocity_x = player_speed
            self.x += player_speed
            self.direction = "RIGHT"

        # ジャンプ処理
        if self.velocity_y == 0 and pyxel.btnp(pyxel.KEY_SPACE) and self.on_ground:
            self.velocity_y = jump_strength
            self.on_ground = False

        if self.velocity_y < 0:
            self.velocity_y += gravity * 3
        else:
            self.velocity_y += gravity
        self.velocity_y = min(self.velocity_y, max_gravity)

        # プレイヤーの位置更新
        self.y += self.velocity_y

    def draw(self):
        if self.direction == "RIGHT":
            pyxel.blt(self.x, self.y, 0, 0, 0, 16, 16, 0)
        elif self.direction == "LEFT":
            pyxel.blt(self.x, self.y, 0, 0, 0, -16, 16, 0)

        # レーザーを描画
        for laser in self.lasers:
            laser.draw()

    def shoot_laser(self, laser_class):
        if self.direction == "RIGHT":
            laser = laser_class(self.x + GRID_SIZE//2, self.y + GRID_SIZE//2, "UP_RIGHT")
        elif self.direction == "LEFT":
            laser = laser_class(self.x + GRID_SIZE//2, self.y + GRID_SIZE//2, "UP_LEFT")
        self.lasers.append(laser) 