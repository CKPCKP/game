import pyxel
from config import FPS, GRID_SIZE
import math, random


class Potion:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.collected = False
        # アニメーション用
        self.anim_timer = 0
        self.start_pos = (x, y)
        self.target_player = None

    def on_collect(self, player):
        # アニメーション開始
        self.target_player = player
        self.anim_timer = FPS  # 1秒間
        self.collected = "kari"
    
    def update(self):
        if self.anim_timer > 0:
            self.anim_timer -= 1
            if self.anim_timer == 0:
                if self.type == "can_be_laser":
                    self.target_player.can_be_laser = "OK"
                else:
                    self.target_player.can_shoot_laser = True


    def draw(self, offset_x=0, offset_y=0):
        u = 0
        if self.type == "can_be_laser":
            u = 1
        if not self.collected:
            pyxel.blt(
                self.x + offset_x,
                self.y + offset_y,
                1,
                u * GRID_SIZE,
                5 * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
                0,
            )
        elif self.anim_timer > 0:
            # 円形軌道でプレイヤー左上へ移動
            t = (FPS - self.anim_timer) / FPS
            sx, sy = self.start_pos
            tx = self.target_player.x
            ty = self.target_player.y
            dx = tx - sx
            dy = ty - sy
            # 半円弧の振幅
            arc_h = GRID_SIZE*4
            y_arc = math.sin(math.pi * t) * arc_h
            cx = int(sx + dx * t)
            cy = int(sy + dy * t - y_arc)
            # ポーション本体を描画
            pyxel.blt(
                cx + offset_x,
                cy + offset_y,
                1,
                u * GRID_SIZE,
                5 * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
                0,
            )
            # エフェクト：小さな円をランダムに散らす
            for _ in range(3):
                ex = cx + offset_x + random.randint(0, GRID_SIZE)
                ey = cy + offset_y + random.randint(0, GRID_SIZE)
                pyxel.circ(ex, ey, 1, 7)

