import pyxel
import config

class Menu:
    def __init__(self):
        pyxel.init(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, fps=config.FPS, title="Menu")
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_RETURN):  # Enterキーでゲームを開始
            self.start_game()

    def draw(self):
        pyxel.cls(0)
        pyxel.text(40, 40, "Laser Shooting Game", pyxel.frame_count % 16)
        pyxel.text(40, 60, "Press Enter to Start", 7)

    def start_game(self):
        import game  # ゲームを開始するためにgameモジュールをインポート
        game.Game()

if __name__ == "__main__":
    Menu()