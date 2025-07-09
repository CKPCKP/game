import pyxel
from config import FPS, GRID_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from death_block import DeathBlock
from save_point import SavePoint


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.lasers = []
        self.direction = "RIGHT"
        self.on_ground = False
        self.alive = True
        self.save_point = (0, 0, 0, 0)
        self.collected_coins = {}
        self.can_shoot_laser = False
        self.can_be_laser = False
        self.laser = None
        self.just_saved = False  # セーブポイントに触れたかどうか
        self.frame = 0
        self.potion_effect_timer = 0
        self.potion_effect_type = None

    def update(self, player_speed, jump_strength, gravity, max_gravity, collidables):
        if self.potion_effect_timer > 0:
            return
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
                            cx = self.x + GRID_SIZE / 2
                            bcx = block.x + block.width / 2
                            if cx < bcx:
                                self.x -= overlap_x
                            else:
                                self.x += overlap_x
                        else:
                            cy = self.y + GRID_SIZE / 2
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
            if (
                self.x < collidable.x + collidable.width
                and self.x + GRID_SIZE > collidable.x
                and self.y < collidable.y + collidable.height
                and self.y + GRID_SIZE > collidable.y
            ):
                if self.velocity_x > 0:
                    self.x = collidable.x - GRID_SIZE
                elif self.velocity_x < 0 or (
                    self.velocity_x == 0 and self.laser == None
                ):
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
            if (
                self.x < collidable.x + collidable.width
                and self.x + GRID_SIZE > collidable.x
                and self.y < collidable.y + collidable.height
                and self.y + GRID_SIZE > collidable.y
            ):
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
        self.frame += 1
        if self.frame >= 30:
            self.frame = 0
        w = GRID_SIZE if self.direction == "RIGHT" else -GRID_SIZE
        v = 3
        if self.can_shoot_laser:
            v = 0
        if self.can_be_laser:
            v = 1
        if self.can_be_laser == "used":
            v = 2
        if not self.laser and self.alive:
            if not self.on_ground:
                frame_index = 2
            elif self.velocity_x != 0:
                frame_index = ((self.frame // 4) % 2) * 2
            else:
                frame_index = self.frame // 15
            pyxel.blt(
                self.x + offset_x,
                self.y + offset_y,
                0,
                v * 16,
                frame_index * GRID_SIZE,
                w,
                GRID_SIZE,
                0,
            )
        elif not self.alive:
            pyxel.blt(
                self.x + offset_x,
                self.y + offset_y,
                0,
                v * 16,
                3 * GRID_SIZE,
                w,
                GRID_SIZE,
                0,
            )

        for laser in self.lasers:
            if laser != self.laser or self.alive:
                laser.draw()

        if self.potion_effect_timer > 0:
            # タイプに応じたメッセージ
            text = "ok"
            if self.potion_effect_type == "can_be_laser":
                text = "can_be_laser"
            elif self.potion_effect_type == "can_shoot_laser":
                text = "can_shoot_laser"
            # プレイヤーの頭上にテキスト表示
            pyxel.text(
                self.x + offset_x,
                self.y - GRID_SIZE // 2 + offset_y,
                text,
                7,
            )
            # タイマーをデクリメント
            self.potion_effect_timer -= 1
            if self.potion_effect_timer == 0:
                self.potion_effect_type = None

    def shoot_laser(self, laser_class):
        if len(self.lasers) >= 2:
            return
        pyxel.play(3, 63, loop=False, resume=True)
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

    def check_get_potion(self, potions):
        for potion in potions:
            if potion.collected:
                return

            player_right = self.x + GRID_SIZE
            player_bottom = self.y + GRID_SIZE
            potion_right = potion.x + GRID_SIZE
            potion_bottom = potion.y + GRID_SIZE

            # 衝突判定
            if (
                potion.x < player_right
                and potion_right > self.x
                and potion.y < player_bottom
                and potion_bottom > self.y
            ):
                potion.on_collect(self)

    def revive(self):
        self.alive = True
        self.lasers = []
        self.laser = None
        self.x = self.save_point[2]
        self.y = self.save_point[3]
        self.velocity_x = 0
        self.velocity_y = 0
        if self.can_be_laser == "used":
            self.can_be_laser = "OK"
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
        self.just_saved = True
        if self.can_be_laser == "used":
            self.can_be_laser = "OK"

    def be_laser(self, laser_class):
        if self.direction == "RIGHT":
            laser = laser_class(
                self.x + GRID_SIZE // 2,
                self.y + GRID_SIZE // 2,
                "UP_RIGHT",
                "transforming_player",
            )
        elif self.direction == "LEFT":
            laser = laser_class(
                self.x + GRID_SIZE // 2,
                self.y + GRID_SIZE // 2,
                "UP_LEFT",
                "transforming_player",
            )
        self.laser = laser
        self.lasers.append(self.laser)
        self.can_be_laser = "used"

    def erase_inactive_laser(self, all=False):
        for laser in list(self.lasers):  # コピーを使って安全に削除
            # 自機に吸着中のレーザーは除外
            if laser == self.laser:
                continue
            # 非アクティブ or 画面外に出たレーザーを除去
            if all or laser.active <= 1:
                #    or laser.x < 0 or laser.x >= SCREEN_WIDTH \
                #    or laser.y < 0 or laser.y >= SCREEN_HEIGHT
                self.lasers.remove(laser)
