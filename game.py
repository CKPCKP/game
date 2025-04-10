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

class Game:
    def __init__(self):
        #pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, fps=FPS, title="Laser Shooting Game")
        pyxel.load("resources/music.pyxres")
        pyxel.playm(0, loop=True)
        pyxel.load("resources/player.pyxres")  # リソースファイルを読み込む
        self.player = Player(SCREEN_HEIGHT)
        self.current_stage_index_x = 16
        self.current_stage_index_y = 0
        self.stages = self.load_stages("stage_map")
        self.paused = False  # ポーズ状態を管理するフラグ
        self.menu_index = 0  # メニューの選択インデックス

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

        # プレイヤーが画面の右端に到達したら次のステージに切り替え
        if self.player.x >= SCREEN_WIDTH - GRID_SIZE:
            self.current_stage_index_x = (self.current_stage_index_x + 1) % len(
                self.stages
            )
            self.player.x -= SCREEN_WIDTH - GRID_SIZE * 2

        if self.player.x < 0:
            self.current_stage_index_x = (self.current_stage_index_x - 1) % len(
                self.stages
            )
            self.player.x += SCREEN_WIDTH - GRID_SIZE * 2

        if self.player.y >= SCREEN_HEIGHT - GRID_SIZE:
            self.current_stage_index_y = (self.current_stage_index_y + 1) % len(
                self.stages
            )
            self.player.y -= SCREEN_HEIGHT - GRID_SIZE * 2

        if self.player.y < 0:
            self.current_stage_index_y = (self.current_stage_index_y - 1) % len(
                self.stages
            )
            self.player.y += SCREEN_HEIGHT - GRID_SIZE * 2

        if self.player.alive == False:
            self.current_stage_index_x = self.player.save_point[1]
            self.current_stage_index_y = self.player.save_point[0]
            self.stages[
                (self.current_stage_index_y, self.current_stage_index_x)
            ].reset()
            self.player.revive()

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