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

class Game:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, fps=FPS, title="Laser Shooting Game")
        pyxel.load("resources/player.pyxres")  # リソースファイルを読み込む
        self.player = Player(SCREEN_HEIGHT)
        self.current_stage_index_x = 0
        self.current_stage_index_y = 0
        self.stages = self.load_stages("stage_map")  # ステージをロード
        
        pyxel.run(self.update, self.draw)

    def load_stages(self, directory):
        stages = {}
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r') as file:
                    x,y = filename.removesuffix(".txt").split("-")
                    stages[(int(x),int(y))] = Stage(file.read().splitlines())
        return stages

    def update(self):
        current_stage = self.stages[(self.current_stage_index_y, self.current_stage_index_x)]
        current_stage.update()
        self.player.update(PLAYER_SPEED, JUMP_STRENGTH, GRAVITY, MAX_GRAVITY, current_stage.collidables)
        

        for laser in self.player.lasers:
            laser.update(current_stage.collidables)

        if pyxel.btnp(pyxel.KEY_Z):
            self.player.shoot_laser(lambda x, y, direction: Laser(x, y, direction, LASER_LIFETIME, LASER_LENGTH, LASER_SPEED))

        # プレイヤーが画面の右端に到達したら次のステージに切り替え
        if self.player.x >= SCREEN_WIDTH - GRID_SIZE:
            self.current_stage_index_x = (self.current_stage_index_x + 1) % len(self.stages)
            self.player.x = GRID_SIZE  # プレイヤーを左端に戻す

        if self.player.x < 0:
            self.current_stage_index_x = (self.current_stage_index_x - 1) % len(self.stages)
            self.player.x = SCREEN_WIDTH - GRID_SIZE * 2
        
        if self.player.y >= SCREEN_HEIGHT - GRID_SIZE:
            self.current_stage_index_y = (self.current_stage_index_y + 1) % len(self.stages)
            self.player.y = GRID_SIZE  # プレイヤーを左端に戻す

        if self.player.y < 0:
            self.current_stage_index_y = (self.current_stage_index_y - 1) % len(self.stages)
            self.player.y = SCREEN_HEIGHT - GRID_SIZE * 2

    def draw(self):
        pyxel.cls(0)
        self.player.draw()
        current_stage = self.stages[(self.current_stage_index_y, self.current_stage_index_x)]
        current_stage.draw()

Game()
