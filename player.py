import pyxel
from config import GRID_SIZE
from save_point import SavePoint


class Player:
    def __init__(self, screen_height):
        self.x = GRID_SIZE
        self.y = screen_height - GRID_SIZE * 4
        self.velocity_x = 0
        self.velocity_y = 0
        self.lasers = []
        self.direction = "RIGHT"
        self.on_ground = False
        self.alive = True
        self.save_point = (0,0,0,0)
        self.collected_coins = {}
        self.can_be_laser = True
        self.laser = None

    def update(self, player_speed, jump_strength, gravity, max_gravity, collidables):
        if self.laser:
            print(self.x, self.y, self.laser.state)
            if self.laser.state == "player":
                self.laser = None
                # self.adjust_position(self)
            else:
                if "UP" in self.laser.direction:
                    self.y = self.laser.y
                else:
                    self.y = self.laser.y - GRID_SIZE
                if "RIGHT" in self.laser.direction:
                    self.x = self.laser.x - GRID_SIZE
                else:
                    self.x = self.laser.x
                self.velocity_x = 0
                self.velocity_y = 0
                velocity_x_yappari = self.velocity_x
                velocity_y_yappari = self.velocity_y
                return
        else:
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
        self.erase_inactive_laser()

    def draw(self):
        if not self.laser:
            if self.direction == "RIGHT":
                pyxel.blt(self.x, self.y, 0, 0, 0, 16, 16, 0)
            elif self.direction == "LEFT":
                pyxel.blt(self.x, self.y, 0, 0, 0, -16, 16, 0)

        # レーザーを描画
        for laser in self.lasers:
            laser.draw()

    def shoot_laser(self, laser_class):
        if len(self.lasers) >= 2:
            return
        if self.direction == "RIGHT":
            laser = laser_class(
                self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, "UP_LEFT"
            )
        elif self.direction == "LEFT":
            laser = laser_class(
                self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, "UP_RIGHT"
            )
        self.lasers.append(laser)
    
    def check_get_coin(self, coins):
        for coin in coins:
            if coin.collected:
                return

            player_right = self.x + GRID_SIZE
            player_bottom = self.y + GRID_SIZE
            coin_right = coin.x + GRID_SIZE
            coin_bottom = coin.y + GRID_SIZE

            # 衝突判定
            if (
                coin.x < player_right
                and coin_right > self.x
                and coin.y < player_bottom
                and coin_bottom > self.y
            ):
                self.collected_coins[coin] = "kari"
                coin.collected = "kari"
            for laser in self.lasers:
                laser.check_get_coin(coin)

    def revive(self):
        self.alive = True
        self.lasers = []
        self.x = self.save_point[2]
        self.y = self.save_point[3]
        self.velocity_x = 0
        self.velocity_y = 0
        for k in self.collected_coins.keys():
            if self.collected_coins[k] == "kari":
                k.collected = ""
                self.collected_coins[k] = ""

    
    def save(self, index_x, index_y, x, y):
        self.save_point = (index_x, index_y, x, y)
        for k in self.collected_coins.keys():
            if self.collected_coins[k] == "kari":
                self.collected_coins[k] = "fixed"
                k.collected = "fixed"
    
    def be_laser(self, laser_class):
        if self.direction == "RIGHT":
            laser = laser_class(
                self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, "UP_RIGHT", "transforming_player"
            )
        elif self.direction == "LEFT":
            laser = laser_class(
                self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, "UP_LEFT", "transforming_player"
            )
        self.laser = laser
        self.lasers.append(self.laser)
    
    def adjust_position():
        return
    
    def erase_inactive_laser(self):
        for laser in self.lasers:
            if laser.active <= 1:
                self.lasers.remove(laser)