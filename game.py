import pyxel
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
        self.current_stage_index = 0
        self.stages = [
            Stage([
                "####################",
                "#                  #",
                "#                  #",
                "#                  #",
                "#                  #",
                "#                  #",
                "#                  #",
                "#                  #",
                "#                  #",
                "#         ###      #",
                "#                  #",
                "#   vvv            #",
                "#                  #",
                "#                  G",
                "####################",
            ]),
            Stage([
                "####################",
                ">                  #",
                ">                  #",
                "#                  #",
                "#                  #",
                "#                  #",
                "#                  #",
                "#        #         #",
                "#                  #",
                "#      #           #",
                "#                  #",
                "#   #              #",
                "#                  #",
                "                   G",
                "####################",
            ]),
            Stage([
                "####################",
                "#                  <",
                "#                  <",
                "#    ###############",
                "#                  #",
                "#                  #",
                "#                  #",
                "#        #         #",
                "#                  #",
                "#      #           #",
                "#                  #",
                "#   #              #",
                "#                  #",
                "                   G",
                "####################",
            ]),
            Stage([
                "####################",
                "#                  #",
                "#  # # # ###  ###  #",
                "#  # # #  #   # #  #",
                "#  # # #  #   ###  #",
                "#   # #   #   #    #",
                "#   # #  ###  #    #",
                "#                  #",
                "#                  #",
                "#                  #",
                "#                  #",
                "#                  #",
                "#                  #",
                "                   #",
                "####################",
            ]),
        ]
        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update(PLAYER_SPEED, JUMP_STRENGTH, GRAVITY, MAX_GRAVITY)
        current_stage = self.stages[self.current_stage_index]
        current_stage.update(self.player)

        for laser in self.player.lasers:
            laser.update(current_stage.blocks)

        if pyxel.btnp(pyxel.KEY_Z):
            self.player.shoot_laser(lambda x, y, direction: Laser(x, y, direction, LASER_LIFETIME, LASER_LENGTH, LASER_SPEED))

        # プレイヤーが画面の右端に到達したら次のステージに切り替え
        if self.player.x >= SCREEN_WIDTH - GRID_SIZE:
            self.current_stage_index = (self.current_stage_index + 1) % len(self.stages)
            self.player.x = GRID_SIZE  # プレイヤーを左端に戻す

        if self.player.x < 0:
            self.current_stage_index = (self.current_stage_index - 1) % len(self.stages)
            self.player.x = SCREEN_WIDTH - GRID_SIZE * 2

    def draw(self):
        pyxel.cls(0)
        self.player.draw()
        current_stage = self.stages[self.current_stage_index]
        current_stage.draw()

Game()
