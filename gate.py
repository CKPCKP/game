import pyxel
from block import Block
from config import GRID_SIZE

class Gate(Block):
    def __init__(self, x, y, width, height, linked_absorbing_blocks):
        super().__init__(x, y, width, height)
        self.linked_absorbing_blocks = linked_absorbing_blocks

    def update(self):
        # 吸収ブロックのフラグを確認
        if any(block.absorbed for block in self.linked_absorbing_blocks):
            self.height = 0  # どれか1つの吸収ブロックが吸収されたらゲートを閉じる
        else:
            self.height = GRID_SIZE  # ゲートを開く

    def draw(self):
        if self.height > 0:
            pyxel.rect(self.x, self.y, self.width, self.height, 14)

    def check_collision(self, player):
        if self.height == 0:
            return  # ゲートが閉じている場合は衝突判定を行わない

        # `Block`クラスの`check_collision`メソッドを呼び出す
        super().check_collision(player)