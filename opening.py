import pyxel
from config import FPS, GRID_SIZE, PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player


class Opening:
    """
    オープニングムービー管理クラス。
    duration_seconds 秒間、または Z/X キー押下でスキップ可能。
    """

    def __init__(self, duration_seconds: int = 5):
        self.timer = FPS * duration_seconds
        self.active = True
        self.player = Player(GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE * 5)
        self.player.on_ground = True
        self.player.direction = "RIGHT"
        self.phase = 0
        self.pause_timer = 0

    def update(self):
        self.timer -= 1
        # タイマー切れ or Z/X で終了
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_X) or self.timer <= 0:
            self.active = False
        if self.phase == 0:
            # 初回歩行：画面中央まで歩く
            self.player.velocity_x = PLAYER_SPEED
            self.player.x += self.player.velocity_x
            if self.player.x >= SCREEN_WIDTH // 3:
                self.phase = 1
                self.pause_timer = FPS * 2  # 1秒間停止
        elif self.phase == 1:
            # 停止中
            self.player.velocity_x = 0
            self.pause_timer -= 1
            if self.pause_timer <= 0:
                self.phase = 2
        else:
            # 再度歩行
            self.player.velocity_x = PLAYER_SPEED
            self.player.x += self.player.velocity_x

    def draw(self):
        # タイルバンク2 の全画面（0,0）〜（SCREEN_WIDTH,SCREEN_HEIGHT）を描画
        pyxel.bltm(0, 0, 0, 0, 0, SCREEN_WIDTH - 80, SCREEN_HEIGHT)
        pyxel.blt(24, 24, 2, 0, 32, 48, 32, 0)
        pyxel.blt(80, 48, 2, 0, 32, 48, 32, 0)
        pyxel.blt(133, 35, 2, 0, 32, 48, 32, 0)
        #pyxel.blt(40, 25, 2, 0, 32, 48, 32, 0)
        self.player.draw()
        pyxel.bltm(SCREEN_WIDTH - 80, 0, 0, SCREEN_WIDTH - 80, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
