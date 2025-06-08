import pyxel
import config
from save_manager import list_slots, load_slot

class Menu:
    def __init__(self):
        # 初期ウィンドウ
        pyxel.init(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, fps=config.FPS, title="Laser Shooting Game")
        # スロット一覧取得
        self.slots = list_slots()      # [ None or dict, … ]
        self.selected_slot = 0         # カーソル位置
        pyxel.run(self.update, self.draw)

    def update(self):
        # 上下キーでスロット選択
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected_slot = (self.selected_slot - 1) % len(self.slots)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selected_slot = (self.selected_slot + 1) % len(self.slots)
        # Enter でゲーム開始
        if pyxel.btnp(pyxel.KEY_RETURN):
            slot_index = self.selected_slot
            slot_data  = self.slots[slot_index]  # None なら新規
            import game
            # Game にスロット情報を渡して起動
            game.Game(slot_index, slot_data)

    def draw(self):
        pyxel.cls(0)
        pyxel.text(30, 20, "Select Save Slot", 7)
        for i, slot in enumerate(self.slots):
            y = 50 + i * 20
            color = 11 if i == self.selected_slot else 7
            if slot is None:
                pyxel.text(40, y, f"Slot {i+1}: Empty", color)
            else:
                sp = slot["save_point"]
                coins = sum(sum(flags) for flags in slot["collected_coins"].values())
                pots  = sum(sum(flags) for flags in slot["collected_potions"].values())
                pyxel.text(40, y, f"Slot {i+1}: Stage{sp['stage']} coins:{coins} pots:{pots}", color)

if __name__ == "__main__":
    Menu()