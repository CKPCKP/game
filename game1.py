import pyxel

# ゲームの設定
STAGE_WIDTH = 9999
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120
GRAVITY = 0.8
JUMP_STRENGTH = -8
PLAYER_SPEED = 2
LASER_SPEED = 2
LASER_LIFETIME = 60
LASER_LENGTH = 16
MAX_GRAVITY = 6

# プレイヤークラス
class Player:
    def __init__(self):
        self.x = 8
        self.y = SCREEN_HEIGHT - 16
        self.velocity_y = 0
        self.lasers = []
        self.direction = "RIGHT"
        self.on_ground = False

    def update(self):
        # 横の移動
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= PLAYER_SPEED
            self.direction = "LEFT"
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += PLAYER_SPEED
            self.direction = "RIGHT"

        # ジャンプ処理
        if pyxel.btnp(pyxel.KEY_SPACE) and self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False

        # 重力の適用
        self.velocity_y += GRAVITY
        self.velocity_y = min(self.velocity_y, MAX_GRAVITY)

        # プレイヤーの位置更新
        self.y += self.velocity_y

    def draw(self):
        # プレイヤーを描画
        pyxel.rect(self.x, self.y, 8, 8, 9)
        # レーザーを描画
        for laser in self.lasers:
            laser.draw()

    def shoot_laser(self):
        if self.direction == "RIGHT":
            laser = Laser(self.x + 4, self.y + 4, "UP_RIGHT")
        elif self.direction == "LEFT":
            laser = Laser(self.x + 4, self.y + 4, "UP_LEFT")
        self.lasers.append(laser)


# レーザークラス
class Laser:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.length = 0
        self.active = LASER_LIFETIME
        self.segments = [(x, y)]

    def update(self, collidables):
        if not self.active:
            return

        # レーザーの生存時間を1減らす
        self.active -= 1

        # 衝突判定を先に行う
        for collidable in collidables:
            if isinstance(collidable, Block):
                if self.check_collision(collidable):
                    # 衝突点を記録
                    self.segments.append((self.x, self.y))

        # レーザーの進行
        if self.direction == "UP_RIGHT":
            self.y -= LASER_SPEED
            self.x += LASER_SPEED
        elif self.direction == "UP_LEFT":
            self.y -= LASER_SPEED
            self.x -= LASER_SPEED
        elif self.direction == "DOWN_RIGHT":
            self.y += LASER_SPEED
            self.x += LASER_SPEED
        elif self.direction == "DOWN_LEFT":
            self.y += LASER_SPEED
            self.x -= LASER_SPEED

        # 新しい位置をセグメントに追加
        self.segments.append((self.x, self.y))

        # レーザーが一定の長さを超えたら古いセグメントを削除
        while len(self.segments) > LASER_LENGTH:
            self.segments.pop(0)

    def draw(self):
        if not self.active:
            return

        # レーザーを描画（セグメントを描画）
        for i in range(len(self.segments) - 1):
            x1, y1 = self.segments[i]
            x2, y2 = self.segments[i + 1]
            pyxel.line(x1, y1, x2, y2, 8)

    def check_collision(self, block):
        # レーザーとブロックの境界
        laser_next_x = (
            self.x + LASER_SPEED if "RIGHT" in self.direction else self.x - LASER_SPEED
        )
        laser_next_y = (
            self.y - LASER_SPEED if "UP" in self.direction else self.y + LASER_SPEED
        )
        block_right = block.x + block.width
        block_bottom = block.y + block.height

        # 衝突しているか確認
        if (
            block.x <= laser_next_x < block_right
            and block.y <= laser_next_y < block_bottom
        ):
            # 反射の処理
            print(self.direction, self.y, laser_next_y, block.y)
            if self.direction == "UP_RIGHT":
                if self.y - LASER_SPEED <= block_bottom <= self.y:
                    self.direction = "DOWN_RIGHT"
                else:
                    self.direction = "UP_LEFT"
            elif self.direction == "UP_LEFT":
                if self.y - LASER_SPEED <= block_bottom <= self.y:
                    self.direction = "DOWN_LEFT"
                else:
                    self.direction = "UP_RIGHT"
            elif self.direction == "DOWN_RIGHT":
                if self.y + LASER_SPEED >= block.y >= self.y:
                    self.direction = "UP_RIGHT"
                else:
                    self.direction = "DOWN_LEFT"
            elif self.direction == "DOWN_LEFT":
                if self.y + LASER_SPEED >= block.y >= self.y:
                    self.direction = "UP_LEFT"
                else:
                    self.direction = "DOWN_RIGHT"
            return True
        return False

# 衝突可能なオブジェクトの基底クラス
class Collidable:
    def check_collision(self, player):
        raise NotImplementedError("このメソッドはサブクラスで実装してください")

# ブロッククラス
class Block(Collidable):
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
            elif player.x + 8 - PLAYER_SPEED <= self.x:
                player.x = self.x - 8

            # 右からの衝突
            elif player.x - PLAYER_SPEED <= block_right:
                player.x = block_right

# ゲームクラス
class Game:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, fps=30, title="Laser Shooting Game")
        self.player = Player()
        self.camera_x = 0
        self.is_scrolling = "STOP"
        self.collidables = [
            Block(0, SCREEN_HEIGHT - 8, STAGE_WIDTH, 8),
            Block(32, SCREEN_HEIGHT - 40, 8, 8),
            Block(40, SCREEN_HEIGHT - 72, 8, 8),
            # 他の衝突可能なオブジェクトをここに追加
        ]
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.is_scrolling == "STOP":
            self.player.update()
            for collidable in self.collidables:
                collidable.update()
                collidable.check_collision(self.player)

            for laser in self.player.lasers:
                laser.update(self.collidables)

            if pyxel.btnp(pyxel.KEY_Z):
                self.player.shoot_laser()

            if not self.camera_x < self.player.x < self.camera_x + SCREEN_WIDTH - 8:
                if self.camera_x < self.player.x:
                    self.is_scrolling = "RIGHT"
                else:
                    self.is_scrolling = "LEFT"

        elif self.is_scrolling == "RIGHT":
            if self.camera_x < self.player.x - 8:
                self.camera_x += PLAYER_SPEED * 2
                if self.camera_x >= self.player.x - 8:
                    self.is_scrolling = "STOP"
        elif self.is_scrolling == "LEFT":
            if self.camera_x > self.player.x - SCREEN_WIDTH + 16:
                self.camera_x -= PLAYER_SPEED * 2
                if self.camera_x <= self.player.x - SCREEN_WIDTH + 16:
                    self.is_scrolling = "STOP"
        pyxel.camera(self.camera_x, 0)

    def draw(self):
        pyxel.cls(0)
        self.player.draw()
        for collidable in self.collidables:
            collidable.draw()


Game()
