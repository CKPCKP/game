import pyxel
from config import FPS, GRID_SIZE, PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player


class Opening:
    """
    オープニングムービー管理クラス。
    duration_seconds 秒間、または Z/X キー押下でスキップ可能。
    """

    def __init__(self, input_mgr, duration_seconds: int = 15):
        self.input = input_mgr
        self.timer = FPS * duration_seconds
        self.active = True
        self.player = Player(self.input, GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE * 5)
        self.player.on_ground = True
        self.player.direction = "RIGHT"
        self.phase = 0
        self.pause_timer = 0
        self.phase2_timer = 0
        self.phase6_timer = 0
        self.scroll_x = 0

    def update(self):
        self.timer -= 1
        # タイマー切れ or Z/X でスキップ
        if self.input.btnp("shoot") or self.input.btnp("transform") or self.timer <= 0:
            self.active = False
        # フェーズごとの動作
        if self.phase == 0:
            # 初回歩行：画面中央まで歩く
            self.player.velocity_x = PLAYER_SPEED
            self.player.x += self.player.velocity_x
            if self.player.x >= SCREEN_WIDTH // 2 + 64:
                # 画面中央に固定してスクロール開始
                self.phase += 1
        elif self.phase == 1:
            # 背景スクロール中（キャラクターは中央で歩き続ける）
            self.player.velocity_x = PLAYER_SPEED
            # スクロール量を更新
            self.scroll_x += self.player.velocity_x
            # 最大スクロール量は左背景幅と同じ（SCREEN_WIDTH - GRID_SIZE*5）
            max_scroll = SCREEN_WIDTH - GRID_SIZE * 16
            if self.scroll_x >= max_scroll:
                # キャラクター停止
                self.player.velocity_x = 0
                self.phase += 1
            self.player.x += self.player.velocity_x
        elif self.phase == 2:
            self.phase2_timer += 1
            if self.phase2_timer >= FPS * 2:
                self.phase += 1
        elif self.phase == 3:
            self.scroll_x += PLAYER_SPEED
            max_scroll = SCREEN_WIDTH - GRID_SIZE * 4
            if self.scroll_x >= max_scroll:
            # スクロール終了
                self.scroll_x = max_scroll
                self.phase += 1
        elif self.phase == 4:
            self.pause_timer += 1
            # スクロール終了後は停止
            self.player.velocity_x = 0
            if self.pause_timer >= FPS * 1:
                self.draw
            if self.pause_timer >= FPS * 2:
                self.phase += 1
        elif self.phase == 5:
            self.player.velocity_x = PLAYER_SPEED
            self.player.x += self.player.velocity_x
            if self.player.x >=  SCREEN_WIDTH + GRID_SIZE * 6:
                self.phase += 1
        elif self.phase == 6:
            self.phase6_timer += 1
            self.player.velocity_x = 0
            if FPS // 2 <= self.phase6_timer <= FPS*2:
                self.player.direction = "LEFT"
            elif FPS*2 < self.phase6_timer <= FPS * 3:
                self.player.direction = "RIGHT"
            elif self.phase6_timer > FPS * 3:
                self.phase += 1
        elif self.phase == 7:
            self.player.velocity_x = PLAYER_SPEED
            self.player.x += self.player.velocity_x
        


    def draw(self):
        offset_x = -self.scroll_x
        # 背景左側
        pyxel.bltm(offset_x, 0, 0, 0, 0, SCREEN_WIDTH + GRID_SIZE * 15, SCREEN_HEIGHT)
        # タイトルパーツ（背景と一緒にスクロール）
        # プレイヤー（オフセット付き）
        #print(self.player.x)
        #self.player.draw(offset_x, 0)
        # 背景右側
        if self.phase < 5:
            pyxel.bltm((SCREEN_WIDTH + GRID_SIZE * 15) + offset_x, 0, 0, SCREEN_WIDTH + GRID_SIZE * 15, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        if self.phase == 2:
            pyxel.blt(
                self.player.x + offset_x,
                self.player.y,
                0,
                3 * 16,
                4 * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
                0,
            )
        elif self.phase == 3:
            pyxel.blt(
                self.player.x + offset_x,
                self.player.y,
                0,
                3 * 16,
                0 * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
                0,
            )
        else:
            self.player.draw(offset_x, 0)
        if self.phase >= 5:
            pyxel.bltm((SCREEN_WIDTH + GRID_SIZE * 15) + offset_x, 0, 0, SCREEN_WIDTH + GRID_SIZE * 15, 0, SCREEN_WIDTH, SCREEN_HEIGHT)