import pyxel
from block import Block
from flag_block import FlagBlock
from death_block import DeathBlock
from config import GRID_SIZE


class Laser:
    def __init__(self, x, y, direction, laser_lifetime, laser_length, laser_speed, state="laser"):
        self.x = int(x)
        self.y = int(y)
        self.direction = direction
        self.length = 0
        self.active = laser_lifetime
        self.segments = [(x, y)]
        self.laser_speed = laser_speed
        self.laser_length = laser_length
        self.state = state
        self.hit_death = False

    def update(self, collidables):
        # レーザーの生存時間を1減らす
        if self.active <= 1:
            if self.state == "laser" or self.state == "player":
                return
            if self.state == "transforming_player":
                self.state = "player"
                return
        self.active -= 1

        # 衝突判定を先に行う
        temp_segments = self.check_collision(collidables)
        self.segments.extend(temp_segments)

        # レーザーが一定の長さを超えたら古いセグメントを削除
        while len(self.segments) > self.laser_length:
            self.segments.pop(0)

    def draw(self):
        if self.active <= 0:
            return

        if self.state == "laser":
            color = 8
        elif self.state == "transforming_player" or self.state == "player":
            color = 13
        # レーザーを描画（セグメントを描画）
        for i in range(len(self.segments) - 1):
            x1, y1 = self.segments[i]
            x2, y2 = self.segments[i + 1]
            pyxel.line(x1, y1, x2, y2, color)

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
                # TRANSPARENT（素通り）ブロックは無視して素通りさせる
                if getattr(block, "collide_with_laser", None) == "TRANSPARENT":
                    continue
                if block.collide_with_laser == "ABSORB":
                    br = block.x + block.width
                    bb = block.y + block.height
                    # 境界 or 内部にいたら吸収
                    if ((block.x <= self.x <= br and self.y in (block.y, bb))
                            or (block.y <= self.y <= bb and self.x in (block.x, br))
                            or (block.x < self.x < br and block.y < self.y < bb)):
                        # DeathBlock にいたらフラグON
                        if isinstance(block, DeathBlock):
                            self.hit_death = True
                        self.active = min(self.active, 1)
                        if isinstance(block, FlagBlock):
                            block.absorbed += 1
                        return temp_segments
                block_right = block.x + block.width
                block_bottom = block.y + block.height

                # 吸収ブロックの場合の特別な処理
                if block.collide_with_laser == "ABSORB":
                    if (
                        (
                            "BOTTOM" in block.absorb_side
                            and self.y == block_bottom
                            and block.x <= self.x <= block_right
                        )
                        or (
                            "TOP" in block.absorb_side
                            and self.y == block.y
                            and block.x <= self.x <= block_right
                        )
                        or (
                            "LEFT" in block.absorb_side
                            and self.x == block.x
                            and block.y <= self.y <= block_bottom
                        )
                        or (
                            "RIGHT" in block.absorb_side
                            and self.x == block_right
                            and block.y <= self.y <= block_bottom
                        )
                    ):
                        self.active = min(self.active, 1)
                        if isinstance(block, FlagBlock):
                            block.absorbed += 1
                        return temp_segments

                if (
                    self.x == block.x
                    and block.y < self.y < block_bottom
                    and "RIGHT" in self.direction
                ):
                    turn_laser(self, "HORIZONTAL")
                elif (
                    self.x == block_right
                    and block.y < self.y < block_bottom
                    and "LEFT" in self.direction
                ):
                    turn_laser(self, "HORIZONTAL")
                elif (
                    self.y == block_bottom
                    and block.x < self.x < block_right
                    and "UP" in self.direction
                ):
                    turn_laser(self, "VERTICAL")
                elif (
                    self.y == block.y
                    and block.x < self.x < block_right
                    and "DOWN" in self.direction
                ):
                    turn_laser(self, "VERTICAL")
                # 隅に当たった場合の処理
                elif self.x in (block.x, block_right) and self.y in (
                    block.y,
                    block_bottom,
                ):
                    collided_blocks_by_corner.append(block)
            if collided_blocks_by_corner:
                if len(collided_blocks_by_corner) == 3:
                    turn_laser(self, "HORIZONTAL")
                    turn_laser(self, "VERTICAL")
                elif len(collided_blocks_by_corner) == 1:
                    if "RIGHT" in self.direction:
                        next_x = self.x + 1
                    else:
                        next_x = self.x - 1
                    if "DOWN" in self.direction:
                        next_y = self.y + 1
                    else:
                        next_y = self.y - 1
                    if (block.x < next_x < block_right
                    and block.y < next_y < block_bottom):
                        turn_laser(self, "HORIZONTAL")
                        turn_laser(self, "VERTICAL")
                elif collided_blocks_by_corner[0].x == collided_blocks_by_corner[1].x:
                    turn_laser(self, "HORIZONTAL")
                elif collided_blocks_by_corner[0].y == collided_blocks_by_corner[1].y:
                    turn_laser(self, "VERTICAL")

        return temp_segments
    
    def check_get_coin(self, coin):
        if coin.collected:
            return False

        laser_right = self.x
        laser_bottom = self.y
        coin_right = coin.x + GRID_SIZE
        coin_bottom = coin.y + GRID_SIZE

        # 衝突判定
        if (
            coin.x < laser_right
            and coin_right > self.x
            and coin.y < laser_bottom
            and coin_bottom > self.y
        ):
            coin.collected = "not_saved"
            return True
        return False 


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
