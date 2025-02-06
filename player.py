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
        self.alive = True

    def update(self, player_speed, jump_strength, gravity, max_gravity, collidables):
        previous_x = self.x
        previous_y = self.y
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
        velocity_y_yappari = self.velocity_y
        velocity_x_yappari = self.velocity_x

        collided_list = []
        for collidable in collidables:
            if collidable.check_collision(self):
                collided_list.append((collidable.x, collidable.y))

        if len(collided_list) == 2:
            if collided_list[0][0] == collided_list[1][0]:
                self.velocity_y = velocity_y_yappari
                self.y = previous_y + velocity_y_yappari
            elif collided_list[0][1] == collided_list[1][1]:
                self.velocity_x = velocity_x_yappari
                self.x = previous_x + velocity_x_yappari

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
            laser = laser_class(
                self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, "UP_LEFT"
            )
        elif self.direction == "LEFT":
            laser = laser_class(
                self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, "UP_RIGHT"
            )
        self.lasers.append(laser)

    def revive(self, stage):
        self.alive = True
        self.x = stage.start_position[0]
        self.y = stage.start_position[1]
        self.velocity_x = 0
        self.velocity_y = 0
