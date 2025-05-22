import pyxel
import os
from player import Player
from laser import Laser
from stage import Stage
from config import (
    FPS,
    GRID_SIZE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GRAVITY,
    JUMP_STRENGTH,
    PLAYER_SPEED,
    LASER_SPEED,
    LASER_LIFETIME,
    LASER_LENGTH,
    MAX_GRAVITY,
)
from save_point import SavePoint  # 追加

DEATH_ANIMATION_FRAMES = FPS // 2
DEATH_SHAKE_AMPLITUDE = 2

class Game:
    def __init__(self):
        #pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, fps=FPS, title="Laser Shooting Game")
        pyxel.load("resources/pyxel_resource.pyxres") # リソースファイルを読み込む
        #pyxel.playm(0, loop=True) 
        self.player = Player(SCREEN_HEIGHT)
        self.current_stage_index_x = 23
        self.current_stage_index_y = 0
        self.stages = self.load_stages("stage_map")
        self.paused = False  # ポーズ状態を管理するフラグ
        self.menu_index = 0  # メニューの選択インデックス
        self.death_timer = 0  # デスアニメーション用タイマー

        pyxel.run(self.update, self.draw)

    def load_stages(self, directory):
        stages = {}
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r") as file:
                    x, y = filename.removesuffix(".txt").split("-")
                    stages[(int(x), int(y))] = Stage(file.read().splitlines(), int(x), int(y))
        return stages

    def update(self):
        if self.death_timer > 0:
            # デスアニメーション中は専用更新
            self.update_death_animation()
        else:
            if pyxel.btnp(pyxel.KEY_P):  # Pキーでポーズ/解除
                self.paused = not self.paused

            if self.paused:
                self.update_pause_menu()
            else:
                self.update_game()

    def update_game(self):
        current_stage = self.stages[
            (self.current_stage_index_y, self.current_stage_index_x)
        ]
        current_stage.update()
        self.player.update(
            PLAYER_SPEED, JUMP_STRENGTH, GRAVITY, MAX_GRAVITY, current_stage.collidables
        )
        self.player.check_get_coin(current_stage.coins)

        for laser in self.player.lasers:
            laser.update(current_stage.collidables)
        # レーザー更新 & DeathBlock 衝突を検知
        for laser in self.player.lasers:
            laser.update(current_stage.collidables)
            if laser.hit_death and laser.state != "laser":
                self.player.alive = False
                break
        
        if self.player.can_be_laser and not self.player.laser and pyxel.btnp(pyxel.KEY_X):
            self.player.be_laser(
                lambda x, y, direction, state: Laser(
                    x, y, direction, LASER_LIFETIME, LASER_LENGTH, LASER_SPEED, state
                )
            )

        if pyxel.btnp(pyxel.KEY_Z):
            self.player.shoot_laser(
                lambda x, y, direction: Laser(
                    x, y, direction, LASER_LIFETIME, LASER_LENGTH, LASER_SPEED
                )
            )

        stage_changed = False
        # プレイヤーが画面の右端に到達したら次のステージに切り替え
        if self.player.x >= SCREEN_WIDTH - GRID_SIZE:
            stage_changed = True
            self.current_stage_index_x = (self.current_stage_index_x + 1) % len(
                self.stages
            )
            self.player.x -= SCREEN_WIDTH - GRID_SIZE * 2

        if self.player.x < 0:
            stage_changed = True
            self.current_stage_index_x = (self.current_stage_index_x - 1) % len(
                self.stages
            )
            self.player.x += SCREEN_WIDTH - GRID_SIZE * 2

        if self.player.y >= SCREEN_HEIGHT - GRID_SIZE:
            stage_changed = True
            self.current_stage_index_y = (self.current_stage_index_y + 1) % len(
                self.stages
            )
            self.player.y -= SCREEN_HEIGHT - GRID_SIZE * 2

        if self.player.y < 0:
            stage_changed = True
            self.current_stage_index_y = (self.current_stage_index_y - 1) % len(
                self.stages
            )
            self.player.y += SCREEN_HEIGHT - GRID_SIZE * 2
        
        if stage_changed:
            self.player.laser = None
            self.player.erase_inactive_laser(all=True)

        # 死亡を検知してデスアニメーションを開始
        if not self.player.alive and self.death_timer == 0:
            self.death_timer = DEATH_ANIMATION_FRAMES

    def update_pause_menu(self):
        if pyxel.btnp(pyxel.KEY_UP):
            self.menu_index = (self.menu_index - 1) % 3
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.menu_index = (self.menu_index + 1) % 3
        if pyxel.btnp(pyxel.KEY_RETURN):
            if self.menu_index == 0:  # Continue
                self.paused = False
            elif self.menu_index == 1:  # Options
                # オプション画面の処理を追加
                pass
            elif self.menu_index == 2:  # Quit
                pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        if self.paused:
            self.draw_pause_menu()
        elif self.death_timer > DEATH_ANIMATION_FRAMES // 2:
            # デスアニメーション中は専用更新
            self.draw_death_animation()
        elif self.death_timer > 0:
            self.draw_death_animation(shake=0)
        else:
            self.draw_game()

    def draw_game(self):
        self.player.draw()
        current_stage = self.stages[
            (self.current_stage_index_y, self.current_stage_index_x)
        ]
        current_stage.draw()

    def draw_pause_menu(self):
        pyxel.text(60, 40, "PAUSE MENU", pyxel.frame_count % 16)
        options = ["Continue", "Options", "Quit"]
        for i, option in enumerate(options):
            color = 7 if i == self.menu_index else 6
            pyxel.text(60, 60 + i * 10, option, color)
    
    def update_death_animation(self):
        # デスアニメーション処理（カウントダウンし、終了時にリスポーン）
        self.death_timer -= 1
        if self.death_timer == 0:
            # リスポーン処理
            self.current_stage_index_x = self.player.save_point[1]
            self.current_stage_index_y = self.player.save_point[0]
            self.stages[
                (self.current_stage_index_y, self.current_stage_index_x)
            ].reset()
            self.player.revive()

    def draw_death_animation(self, shake=DEATH_SHAKE_AMPLITUDE):
        dx = pyxel.rndi(-shake, shake)
        dy = pyxel.rndi(-shake, shake)
        # オフセット付きでステージ＆プレイヤーを描画
        self.draw_game_with_offset(dx, dy)

    # オフセット付き描画用メソッド
    def draw_game_with_offset(self, offset_x, offset_y):
        self.player.draw(offset_x, offset_y)
        current_stage = self.stages[
            (self.current_stage_index_y, self.current_stage_index_x)
        ]
        current_stage.draw(offset_x, offset_y)