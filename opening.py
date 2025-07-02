import pyxel
from config import FPS, PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player

class Opening:
    """
    オープニングムービー管理クラス。
    duration_seconds 秒間、または Z/X キー押下でスキップ可能。
    """
    def __init__(self, duration_seconds: int = 3):
        self.timer = FPS * duration_seconds
        self.active = True
        self.player = Player(SCREEN_HEIGHT)
        self.player.on_ground = True
        self.player.direction = "RIGHT"

    def update(self):
        self.timer -= 1
        # タイマー切れ or Z/X で終了
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_X) or self.timer <= 0:
            self.active = False
        self.player.velocity_x = PLAYER_SPEED
        self.player.x += self.player.velocity_x

    def draw(self):
        # タイルバンク2 の全画面（0,0）〜（SCREEN_WIDTH,SCREEN_HEIGHT）を描画
        pyxel.bltm(0, 0, 0, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player.draw()