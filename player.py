import pyxel
from config import GRID_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from death_block import DeathBlock
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
        self.save_point = (0, 0, 0, 0)
        self.collected_coins = {}
        self.can_be_laser = False
        self.laser = None

    def update(self, player_speed, jump_strength, gravity, max_gravity, collidables):
        if self.laser:
            # 吸着中は移動ストップ＆位置合わせだけ
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
                for block in collidables:
                    if not getattr(block, "collide_with_player", False):
                        continue
                    pl, pr = self.x, self.x + GRID_SIZE
                    pt, pb = self.y, self.y + GRID_SIZE
                    bl, br = block.x, block.x + block.width
                    bt, bb = block.y, block.y + block.height
                    # AABB 判定
                    if pl < br and pr > bl and pt < bb and pb > bt:
                        overlap_x = min(pr, br) - max(pl, bl)
                        overlap_y = min(pb, bb) - max(pt, bt)
                        # 小さいほうの方向へだけ移動
                        if overlap_x < overlap_y:
                            cx  = self.x + GRID_SIZE / 2
                            bcx = block.x + block.width / 2
                            if cx < bcx:
                                self.x -= overlap_x
                            else:
                                self.x += overlap_x
                        else:
                            cy  = self.y + GRID_SIZE / 2
                            bcy = block.y + block.height / 2
                            if cy < bcy:
                                self.y -= overlap_y
                            else:
                                self.y += overlap_y
                self.erase_inactive_laser()
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
                elif self.velocity_x < 0 or (self.velocity_x == 0 and self.laser == None):
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

    def draw(self, offset_x=0, offset_y=0):
        if not self.laser:
            if self.direction == "RIGHT":
                pyxel.blt(self.x + offset_x, self.y + offset_y, 0, 0, 0, 16, 16, 0)
            else:
                pyxel.blt(self.x + offset_x, self.y + offset_y, 0, 0, 0, -16, 16, 0)
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

    def check_get_potion(self, can_be_laser_potions):
        for can_be_laser_potion in can_be_laser_potions:
            if can_be_laser_potion.collected:
                return

            player_right = self.x + GRID_SIZE
            player_bottom = self.y + GRID_SIZE
            can_be_laser_potion_right = can_be_laser_potion.x + GRID_SIZE
            can_be_laser_potion_bottom = can_be_laser_potion.y + GRID_SIZE

            # 衝突判定
            if can_be_laser_potion.x < player_right and can_be_laser_potion_right > self.x and can_be_laser_potion.y < player_bottom and can_be_laser_potion_bottom > self.y:
                self.can_be_laser = "OK"
                can_be_laser_potion.collected = True

    def revive(self):
        self.alive = True
        self.lasers = []
        self.laser = None
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
        self.can_be_laser = "used"

    def adjust_position(self):
        self.x = (self.x // GRID_SIZE) * GRID_SIZE
        self.y = (self.y // GRID_SIZE) * GRID_SIZE
        return

    def erase_inactive_laser(self, all=False):
        for laser in list(self.lasers):  # コピーを使って安全に削除
            # 自機に吸着中のレーザーは除外
            if laser == self.laser:
                continue
            # 非アクティブ or 画面外に出たレーザーを除去
            if all or laser.active <= 1 \
               or laser.x < 0 or laser.x >= SCREEN_WIDTH \
               or laser.y < 0 or laser.y >= SCREEN_HEIGHT:
                self.lasers.remove(laser)