import pyxel
from block import Block
from flag_block import FlagBlock

class Laser:
    def __init__(self, x, y, direction, laser_lifetime, laser_length, laser_speed):
        self.x = int(x)
        self.y = int(y)
        self.direction = direction
        self.length = 0
        self.active = laser_lifetime
        self.segments = [(x, y)]
        self.laser_speed = laser_speed
        self.laser_length = laser_length

    def update(self, collidables):
        # レーザーの生存時間を1減らす
        if not self.active:
            return
        self.active -= 1

        # 衝突判定を先に行う
        temp_segments = self.check_collision(collidables)
        self.segments.extend(temp_segments)

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

    def check_collision(self, blocks):
        temp_segments = []
        collided_blocks_by_corner = []
        for i in range(self.laser_speed):
    
            if self.direction == "UP_RIGHT":
                temp_segments.append((self.x + 1, self.y - 1))
            elif self.direction == "UP_LEFT":
                temp_segments.append((self.x - 1, self.y - 1))
            elif self.direction == "DOWN_RIGHT":
                temp_segments.append((self.x + 1, self.y + 1))
            elif self.direction == "DOWN_LEFT":
                temp_segments.append((self.x - 1, self.y + 1))
            self.x = temp_segments[i][0]
            self.y = temp_segments[i][1]
            for block in blocks:
                if block.collide_with_laser == "TRANSPARENT":
                    continue
                block_right = block.x + block.width
                block_bottom = block.y + block.height

                # 吸収ブロックの場合の特別な処理
                if block.collide_with_laser == "ABSORB":
                    if ('BOTTOM' in block.absorb_side and self.y == block_bottom and block.x <= self.x <= block_right) or \
                       ('TOP' in block.absorb_side and self.y == block.y and block.x <= self.x <= block_right) or \
                       ('LEFT' in block.absorb_side and self.x == block.x and block.y <= self.y <= block_bottom) or \
                       ('RIGHT' in block.absorb_side and self.x == block_right and block.y <= self.y <= block_bottom):
                        self.active = min(self.active, 1)
                        if isinstance(block, FlagBlock):
                            block.absorbed = True
                        print(temp_segments)
                        return temp_segments

                if self.x == block.x and block.y < self.y < block_bottom and "RIGHT" in self.direction:
                    turn_laser(self, "HORIZONTAL")
                elif self.x == block_right and block.y < self.y < block_bottom and "LEFT" in self.direction:
                    turn_laser(self, "HORIZONTAL")
                elif self.y == block_bottom and block.x < self.x < block_right and "UP" in self.direction:
                    turn_laser(self, "VERTICAL")
                elif self.y == block.y and block.x < self.x < block_right and "DOWN" in self.direction:
                    turn_laser(self, "VERTICAL")
                # 隅に当たった場合の処理
                elif self.x in (block.x, block_right) and self.y in (block.y, block_bottom):
                    collided_blocks_by_corner.append(block)
            if collided_blocks_by_corner:
                if len(collided_blocks_by_corner) in (1,3):
                    turn_laser(self, "HORIZONTAL")
                    turn_laser(self, "VERTICAL")
                elif collided_blocks_by_corner[0].x == collided_blocks_by_corner[1].x:
                    turn_laser(self, "HORIZONTAL")
                elif collided_blocks_by_corner[0].y == collided_blocks_by_corner[1].y:
                    turn_laser(self, "VERTICAL")

        return temp_segments

def turn_laser(self, direction):
    if direction == "HORIZONTAL":
        if self.direction == "UP_RIGHT":
            self.direction = "UP_LEFT"
        elif self.direction == "UP_LEFT":
            self.direction = "UP_RIGHT"
        elif self.direction == "DOWN_RIGHT":
            self.direction = "DOWN_LEFT"
        elif self.direction == "DOWN_LEFT":
            self.direction = "DOWN_RIGHT"
    elif direction == "VERTICAL":
        if self.direction == "UP_RIGHT":
            self.direction = "DOWN_RIGHT"
        elif self.direction == "UP_LEFT":
            self.direction = "DOWN_LEFT"
        elif self.direction == "DOWN_RIGHT":
            self.direction = "UP_RIGHT"
        elif self.direction == "DOWN_LEFT":
            self.direction = "UP_LEFT"
