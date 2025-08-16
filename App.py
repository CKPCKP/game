import pyxel
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game import Game
from menu import Menu
from input_manager import InputManager

class App:
    def __init__(self):
        self.input_mgr = InputManager()
        self.menu = Menu(self.input_mgr)    # init/run は呼ばない
        self.game = None
        self.state = "menu"

    def update(self):
        if self.state == "menu":
            result = self.menu.update()
            if result is not None:
                slot_index, slot_data = result
                self.state = "game"
                self.game = Game(self.input_mgr, slot_index, slot_data)
                self.game.update()
        elif self.state == "game":
            finished = self.game.update()
            if finished:
                # ゲーム終了 → メニューへ戻す
                self.state = "menu"
                self.menu.reload_slots()

    def draw(self):
        if self.state == "menu":
            self.menu.draw()
        else:
            self.game.draw()

if __name__ == "__main__":
    # アプリ起動部：一度だけ初期化してループ開始
    pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, fps=FPS, title="LASERIN")
    pyxel.load("resources/pyxel_resource.pyxres")
    app = App()
    pyxel.run(app.update, app.draw)