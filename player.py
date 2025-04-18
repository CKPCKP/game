import pyxel
from config import GRID_SIZE
from save_point import SavePoint


class Player:
    def __init__(self, screen_height):
        self.x = GRID_SIZE
        self.y = screen_height - GRID_SIZE * 10
        self.velocity_x = 0
        self.velocity_y = 0
        self.lasers = []
        self.direction = "RIGHT"
        self.on_ground = False
        self.alive = True
        self.save_point = (0, 0, 0, 0)
        self.collected_coins = {}
        self.can_be_laser = True
        self.laser = None

    def update(self, player_speed, jump_strength, gravity, max_gravity, collidables):
        previous_x = self.x
        previous_y = self.y
        if self.laser:
            self.velocity_x = 0
            self.velocity_y = 0
            if self.laser.state == "player":
                self.laser = None
            else:
                # レーザーに吸着
                if "UP" in self.laser.direction:
                    self.y = self.laser.y
                else:
                    self.y = self.laser.y - GRID_SIZE
                if "RIGHT" in self.laser.direction:
                    self.x = self.laser.x - GRID_SIZE
                else:
                    self.x = self.laser.x
                return
                # 水平移動
        self.velocity_x = 0
        if pyxel.btn(pyxel.KEY_LEFT):
            self.velocity_x = -player_speed
            self.direction = "LEFT"
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.velocity_x = player_speed
            self.direction = "RIGHT"
        self.x += self.velocity_x

        # 水平衝突解消
        for collidable in collidables:
            collidable.check_collision(self)  # SavePoint等の副作用処理
            if not getattr(collidable, "collide_with_player", False):
                continue
            # AABB 判定
            if (self.x < collidable.x + collidable.width and
                self.x + GRID_SIZE > collidable.x and
                self.y < collidable.y + collidable.height and
                self.y + GRID_SIZE > collidable.y):
                if self.velocity_x > 0:
                    self.x = collidable.x - GRID_SIZE
                elif self.velocity_x < 0:
                    self.x = collidable.x + collidable.width
                self.velocity_x = 0

        # ジャンプ＆重力
        if self.on_ground and pyxel.btnp(pyxel.KEY_SPACE):
            self.velocity_y = jump_strength
            self.on_ground = False
        if self.velocity_y < 0:
            self.velocity_y += gravity * 3
        else:
            self.velocity_y += gravity
        self.velocity_y = min(self.velocity_y, max_gravity)

        # 垂直移動
        self.y += self.velocity_y
        self.on_ground = False

        # 垂直衝突解消
        for collidable in collidables:
            collidable.check_collision(self)
            if not getattr(collidable, "collide_with_player", False):
                continue
            if (self.x < collidable.x + collidable.width and
                self.x + GRID_SIZE > collidable.x and
                self.y < collidable.y + collidable.height and
                self.y + GRID_SIZE > collidable.y):
                if self.velocity_y > 0:
                    # 床接地
                    self.y = collidable.y - GRID_SIZE
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    # 天井衝突
                    self.y = collidable.y + collidable.height
                    self.velocity_y = 0

        self.erase_inactive_laser()

    def draw(self):
        if not self.laser:
            if self.direction == "RIGHT":
                pyxel.blt(self.x, self.y, 0, 0, 0, 16, 16, 0)
            elif self.direction == "LEFT":
                pyxel.blt(self.x, self.y, 0, 0, 0, -16, 16, 0)

        # レーザーを描画する
        for laser in self.lasers:
            laser.draw()

    def shoot_laser(self, laser_class):
        if len(self.lasers) >= 2:
            return
        pyxel.play(3, 63, loop=False, resume=True)
        if self.direction == "RIGHT":
            laser = laser_class(self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, "UP_LEFT")
        elif self.direction == "LEFT":
            laser = laser_class(self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, "UP_RIGHT")
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
            if coin.x < player_right and coin_right > self.x and coin.y < player_bottom and coin_bottom > self.y:
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
            laser = laser_class(self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, "UP_RIGHT", "transforming_player")
        elif self.direction == "LEFT":
            laser = laser_class(self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2, "UP_LEFT", "transforming_player")
        self.laser = laser
        self.lasers.append(self.laser)

    def adjust_position(self):
        return

    def erase_inactive_laser(self, all=False):
        for laser in self.lasers:
            if all or laser.active <= 1:
                self.lasers.remove(laser)