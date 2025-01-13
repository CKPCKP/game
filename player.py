import pyxel

class Player:
    def __init__(self, screen_height):
        self.x = 8
        self.y = screen_height - 16
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
        if pyxel.btnp(pyxel.KEY_SPACE) and self.on_ground:
            self.velocity_y = jump_strength
            self.on_ground = False

        # 重力の適用
        self.velocity_y += gravity
        self.velocity_y = min(self.velocity_y, max_gravity)

        # プレイヤーの位置更新
        self.y += self.velocity_y

    def draw(self):
        # プレイヤーを描画
        pyxel.rect(self.x, self.y, 8, 8, 9)
        # レーザーを描画
        for laser in self.lasers:
            laser.draw()

    def shoot_laser(self, laser_class):
        if self.direction == "RIGHT":
            laser = laser_class(self.x + 4, self.y + 4, "UP_RIGHT")
        elif self.direction == "LEFT":
            laser = laser_class(self.x + 4, self.y + 4, "UP_LEFT")
        self.lasers.append(laser) 