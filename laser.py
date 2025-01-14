import pyxel
from block import Block
from absorbing_block import AbsorbingBlock

class Laser:
    def __init__(self, x, y, direction, laser_lifetime, laser_length, laser_speed):
        self.x = x
        self.y = y
        self.direction = direction
        self.length = 0
        self.active = laser_lifetime
        self.segments = [(x, y)]
        self.laser_speed = laser_speed
        self.laser_length = laser_length

    def update(self, collidables):
        if not self.active:
            return

        # レーザーの生存時間を1減らす
        self.active -= 1

        # 衝突判定を先に行う
        for collidable in collidables:
            if self.check_collision(collidable):
                # 衝突点を記録
                self.segments.append((self.x, self.y))

        # レーザーの進行
        if self.direction == "UP_RIGHT":
            self.y -= self.laser_speed
            self.x += self.laser_speed
        elif self.direction == "UP_LEFT":
            self.y -= self.laser_speed
            self.x -= self.laser_speed
        elif self.direction == "DOWN_RIGHT":
            self.y += self.laser_speed
            self.x += self.laser_speed
        elif self.direction == "DOWN_LEFT":
            self.y += self.laser_speed
            self.x -= self.laser_speed

        # 新しい位置をセグメントに追加
        self.segments.append((self.x, self.y))

        # レーザーが一定の長さを超えたら古いセグメントを削除
        while len(self.segments) > self.laser_length:
            self.segments.pop(0)

    def draw(self):
        if not self.active:
            return

        # レーザーを描画（セグメントを描画）
        for i in range(len(self.segments) - 1):
            x1, y1 = self.segments[i]
            x2, y2 = self.segments[i + 1]
            pyxel.line(x1, y1, x2, y2, 8)

    def check_collision(self, block):
        # レーザーとブロックの境界
        laser_next_x = (
            self.x + self.laser_speed if "RIGHT" in self.direction else self.x - self.laser_speed
        )
        laser_next_y = (
            self.y - self.laser_speed if "UP" in self.direction else self.y + self.laser_speed
        )
        block_right = block.x + block.width
        block_bottom = block.y + block.height

        # 吸収ブロックの場合の特別な処理
        if isinstance(block, AbsorbingBlock):
            if (
                block.x <= laser_next_x < block_right
                and block.y <= laser_next_y < block_bottom
            ):
                if block.absorb_side == 'BOTTOM' and self.y - self.laser_speed <= block_bottom <= self.y:
                    block.absorbed = True
                    self.active = 0
                    return True
                elif block.absorb_side == 'TOP' and self.y <= block.y <= self.y + self.laser_speed:
                    block.absorbed = True
                    self.active = 0
                    return True
                elif block.absorb_side == 'LEFT' and self.x <= block.x <= self.x + self.laser_speed:
                    block.absorbed = True
                    self.active = 0
                    return True
                elif block.absorb_side == 'RIGHT' and self.x - self.laser_speed <= block_right <= self.x:
                    block.absorbed = True
                    self.active = 0
                    return True

        # 通常のブロックに対する衝突判定
        if (
            block.x <= laser_next_x < block_right
            and block.y <= laser_next_y < block_bottom
        ):
            # 反射の処理
            if self.direction == "UP_RIGHT":
                if self.y - self.laser_speed <= block_bottom <= self.y:
                    self.direction = "DOWN_RIGHT"
                else:
                    self.direction = "UP_LEFT"
            elif self.direction == "UP_LEFT":
                if self.y - self.laser_speed <= block_bottom <= self.y:
                    self.direction = "DOWN_LEFT"
                else:
                    self.direction = "UP_RIGHT"
            elif self.direction == "DOWN_RIGHT":
                if self.y + self.laser_speed >= block.y >= self.y:
                    self.direction = "UP_RIGHT"
                else:
                    self.direction = "DOWN_LEFT"
            elif self.direction == "DOWN_LEFT":
                if self.y + self.laser_speed >= block.y >= self.y:
                    self.direction = "UP_LEFT"
                else:
                    self.direction = "DOWN_RIGHT"
            return True
        return False 