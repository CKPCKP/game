import pyxel
from config import GRID_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, FPS
from save_manager import delete_slot, list_slots, load_slot


class Menu:
    def __init__(self):
        # 初期ウィンドウ
        pyxel.init(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            fps=FPS,
            title="Laser Shooting Game",
        )
        pyxel.load("resources/pyxel_resource.pyxres")
        # スロット一覧取得
        self.slots = list_slots()  # [ None or dict, … ]
        self.selected_slot = 0
        self.confirming_delete = False
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
            slot_data = self.slots[slot_index]  # None なら新規
            import game

            # Game にスロット情報を渡して起動
            game.Game(slot_index, slot_data)

        if pyxel.btnp(pyxel.KEY_C):
            if self.slots[self.selected_slot] is not None:
                if not self.confirming_delete:
                    # 初回押下で確認モードへ
                    self.confirming_delete = True
                else:
                    # 再度押下で削除して一覧更新
                    delete_slot(self.selected_slot)
                    self.slots = list_slots()
                    self.confirming_delete = False

    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(0, 0, 1, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0)
        pyxel.rect(0, 192, SCREEN_WIDTH, 128, 1)
        pyxel.text(150, 200, "Select Save Slot", 7)
        for i, slot in enumerate(self.slots):
            y = 220 + i * 17
            color = 11 if i == self.selected_slot else 7
            if slot is None:
                pyxel.text(135, y, f"Slot {i + 1}: Empty", color)
            else:
                sp = slot["save_point"]
                coins = sum(
                    sum([1 if flags == "true" else 0])
                    for flags in slot["collected_coins"].values()
                )
                pyxel.text(
                    135,
                    y,
                    f"Slot {i + 1}: {str(sp['stage'][1]).zfill(3)}           {coins}",
                    color,
                )
                if "player_can_shoot_laser" in slot and slot["player_can_shoot_laser"]: 
                    pyxel.blt(
                        185,
                        y - 1,
                        1,
                        0 * GRID_SIZE,
                        6 * GRID_SIZE,
                        GRID_SIZE //2,
                        GRID_SIZE //2 ,
                        0,
                    )
                if slot["player_can_be_laser"]: 
                    pyxel.blt(
                        195,
                        y - 1,
                        1,
                        0.5 * GRID_SIZE,
                        6 * GRID_SIZE,
                        GRID_SIZE //2,
                        GRID_SIZE //2,
                        0,
                    )
                pyxel.circ(
                    215,
                    y + 2,
                    3,
                    10,
                )
        
        if self.confirming_delete and self.slots[self.selected_slot] is not None:
            pyxel.text(125, 270, "Press C again to confirm delete", 8)


if __name__ == "__main__":
    Menu()
