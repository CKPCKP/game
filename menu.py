import pyxel
from config import GRID_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, FPS
from save_manager import delete_slot, list_slots, load_slot


class Menu:
    def __init__(self, input_mgr):
        self.input = input_mgr
        self.font = pyxel.Font("resources/umplus_j10r.bdf")
        # スロット一覧取得
        self.slots = list_slots()  # [ None or dict, … ]
        self.selected_slot = 0
        self.confirming_delete = False
        self.selected_slot = 0
        self.confirming_delete = False

    def update(self):
        # 上下キーでスロット選択
        if self.input.btnp("up"):
            self.confirming_delete = False
            self.selected_slot = (self.selected_slot - 1) % len(self.slots)
        if self.input.btnp("down"):
            self.confirming_delete = False
            self.selected_slot = (self.selected_slot + 1) % len(self.slots)
        # Enter でゲーム開始
        if self.input.btnp("confirm"):
            self.confirming_delete = False
            slot_index = self.selected_slot
            slot_data = self.slots[slot_index]  # None なら新規
            return slot_index, slot_data

        if self.input.btnp("delete"):
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
        for i, slot in enumerate(self.slots):
            y = 210 + i * 17
            color = 11 if i == self.selected_slot else 7
            if slot is None:
                self.write_text("CENTER", f"Slot {i + 1}: Empty", y, color)
            else:
                sp = slot["save_point"]
                coins = sum(
                    sum([1 if flags == ["fixed"] else 0])
                    for flags in slot["collected_coins"].values()
                )
                self.write_text(
                    "CENTER",
                    f"Slot {i + 1}: {str(sp['stage'][1]).zfill(3)}           {coins}",
                    y, 
                    color
                )
                if "player_can_shoot_laser" in slot and slot["player_can_shoot_laser"]: 
                    pyxel.blt(
                        200,
                        y + 2,
                        1,
                        0 * GRID_SIZE,
                        6 * GRID_SIZE,
                        GRID_SIZE //2,
                        GRID_SIZE //2 ,
                        0,
                    )
                if slot["player_can_be_laser"]: 
                    pyxel.blt(
                        215,
                        y + 2,
                        1,
                        0.5 * GRID_SIZE,
                        6 * GRID_SIZE,
                        GRID_SIZE //2,
                        GRID_SIZE //2,
                        0,
                    )
                pyxel.circ(
                    245,
                    y + 5,
                    3,
                    10,
                )
        
        self.write_text("CENTER", "delete: C -> C", 270, 8)
        if self.confirming_delete:
            self.write_text("CENTER", "        C     ", 270, 11)

    def write_text(self, align: str, text: str, y: int = 10, col: int = 7):
        """指定した整列方法でテキストを描画する

        align: "LEFT", "CENTER", "RIGHT"
        text: 描画する文字列
        y: 縦位置（省略時は10）
        col: 色（省略時は7=白）
        """
        text_width = self.font.text_width(text)

        if align == "LEFT":
            x = 0
        elif align == "CENTER":
            x = (SCREEN_WIDTH - text_width) // 2
        elif align == "RIGHT":
            x = SCREEN_WIDTH - text_width
        else:
            raise ValueError("align は 'LEFT', 'CENTER', 'RIGHT' のいずれかで指定してください")

        pyxel.text(x, y, text, col, self.font)

    def reload_slots(self):
        """セーブスロット一覧を再読み込みしてメニュー状態をリセット"""
        self.slots = list_slots()
        self.selected_slot = 0
        self.confirming_delete = False

if __name__ == "__main__":
    Menu()
