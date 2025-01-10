import pyxel

# ゲームの設定
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120
GRAVITY = 0.8
JUMP_STRENGTH = -8
PLAYER_SPEED = 2
LASER_SPEED = 4
LASER_LIFETIME = 15
LASER_LENGTH = 16  # レーザーの最大長さ
MAX_GRAVITY = 6  # 最大落下速度を設定


# プレイヤークラス
class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 16
        self.velocity_y = 0
        self.lasers = []

    def update(self):
        # 横の移動
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += PLAYER_SPEED

        # ジャンプ処理
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.velocity_y = JUMP_STRENGTH

        # 重力の適用
        self.velocity_y += GRAVITY
        self.velocity_y = min(self.velocity_y, MAX_GRAVITY)  # 最大落下速度を適用

        # プレイヤーの位置更新
        self.y += self.velocity_y

        # レーザーの更新
        for laser in self.lasers:
            laser.update()

    def draw(self):
        # プレイヤーを描画
        pyxel.rect(self.x, self.y, 8, 8, 9)  # プレイヤーを四角で描画
        # レーザーを描画
        for laser in self.lasers:
            laser.draw()

    def shoot_laser(self, direction):
        # レーザー発射
        laser = Laser(self.x + 4, self.y + 4, direction)
        self.lasers.append(laser)


# レーザークラス
class Laser:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # 上、下、左、右
        self.length = 0  # 現在の長さ
        self.active = LASER_LIFETIME

    def update(self):
        if not self.active:
            return

        # レーザーの進行
        if self.direction == "UP":
            self.y -= LASER_SPEED
        elif self.direction == "DOWN":
            self.y += LASER_SPEED
        elif self.direction == "LEFT":
            self.x -= LASER_SPEED
        elif self.direction == "RIGHT":
            self.x += LASER_SPEED

        # レーザーが一定の長さに達したら停止
        self.length = min(LASER_LENGTH, self.length + LASER_SPEED)

        # レーザーの生存時間を1減らす
        self.active -= 1

    def draw(self):
        if not self.active:
            return

        # レーザーを描画（長さを表示）
        if self.direction == "UP":
            pyxel.line(self.x, self.y, self.x, self.y - self.length, 8)
        elif self.direction == "DOWN":
            pyxel.line(self.x, self.y, self.x, self.y + self.length, 8)
        elif self.direction == "LEFT":
            pyxel.line(self.x, self.y, self.x - self.length, self.y, 8)
        elif self.direction == "RIGHT":
            pyxel.line(self.x, self.y, self.x + self.length, self.y, 8)


class Block:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def update(self):
        # ブロックは動かない場合、特に更新処理は不要
        pass

    def draw(self):
        # ブロックを描画
        pyxel.rect(self.x, self.y, self.width, self.height, 11)  # ブロックを四角で描画

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
        self.blocks = [
            Block(0, SCREEN_HEIGHT - 8, SCREEN_WIDTH, 8),
            Block(32, SCREEN_HEIGHT - 40, 8, 8),
            Block(40, SCREEN_HEIGHT - 72, 8, 8),
        ]
        pyxel.run(self.update, self.draw)

    def update(self):
        # プレイヤーの更新
        self.player.update()
        for block in self.blocks:
            block.update()
            block.check_collision(self.player)

        # レーザー発射
        if pyxel.btnp(pyxel.KEY_W):  # 上
            self.player.shoot_laser("UP")
        if pyxel.btnp(pyxel.KEY_S):  # 下
            self.player.shoot_laser("DOWN")
        if pyxel.btnp(pyxel.KEY_A):  # 左
            self.player.shoot_laser("LEFT")
        if pyxel.btnp(pyxel.KEY_D):  # 右
            self.player.shoot_laser("RIGHT")

    def draw(self):
        pyxel.cls(0)
        self.player.draw()
        for block in self.blocks:
            block.draw()


Game()
