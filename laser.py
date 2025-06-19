import pyxel
from block import Block
from flag_block import FlagBlock
from death_block import DeathBlock
from config import GRID_SIZE
import random
import math

# ─── パーティクル定義 ───────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, vx, vy, lifetime, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self):
        if self.lifetime > 0:
            pyxel.pset(int(self.x), int(self.y), self.color)

def direction_to_angle(dir_str1, dir_str2):
    if "UP" in dir_str1 and "DOWN" in dir_str2:
        return math.pi/2
    if "DOWN" in dir_str1 and "UP" in dir_str2:
        return -math.pi/2
    if "LEFT" in dir_str1 and "RIGHT" in dir_str2:
        return 0
    if "RIGHT" in dir_str1 and "LEFT" in dir_str2:
        return math.pi
    return 0

def spawn_particles(p_list, x, y, base_angle, color,
                    count=5, spread=math.pi/8,
                    speed_min=0.5, speed_max=1.5,
                    life_min=5, life_max=10):
    for _ in range(count):
        a = base_angle + random.uniform(-spread, spread)
        s = random.uniform(speed_min, speed_max)
        vx = math.cos(a) * s
        vy = math.sin(a) * s
        life = random.randint(life_min, life_max)
        p_list.append(Particle(x, y, vx, vy, life, color))



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
        self.particles = []
        p_color = 8 if state == "laser" else 13

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
        
        for p in list(self.particles):
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

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

        for p in self.particles:
            p.draw()

    def check_collision(self, blocks):
        temp_segments = []
        for i in range(self.laser_speed):
            collided_blocks_by_corner = []
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
                br = block.x + block.width
                bb = block.y + block.height
                if block.collide_with_laser == "ABSORB":
                    # 境界 or 内部にいたら吸収
                    if ((block.x <= self.x <= br and self.y in (block.y, bb))
                            or (block.y <= self.y <= bb and self.x in (block.x, br))
                            or (block.x < self.x < br and block.y < self.y < bb)):
                        # DeathBlock にいたらフラグON
                        if isinstance(block, DeathBlock):
                            self.hit_death = True
                        self.active = min(self.active, 1)
                        if isinstance(block, FlagBlock):
                            if (
                                (
                                    "BOTTOM" in block.absorb_side
                                    and self.y == bb
                                    and block.x <= self.x <= br
                                )
                                or (
                                    "TOP" in block.absorb_side
                                    and self.y == block.y
                                    and block.x <= self.x <= br
                                )
                                or (
                                    "LEFT" in block.absorb_side
                                    and self.x == block.x
                                    and block.y <= self.y <= bb
                                )
                                or (
                                    "RIGHT" in block.absorb_side
                                    and self.x == br
                                    and block.y <= self.y <= bb
                                )
                            ):
                                block.absorbed += 1
                        return temp_segments

                if (
                    self.x == block.x
                    and block.y < self.y < bb
                    and "RIGHT" in self.direction
                ):
                    turn_laser(self, "HORIZONTAL", block)
                elif (
                    self.x == br
                    and block.y < self.y < bb
                    and "LEFT" in self.direction
                ):
                    turn_laser(self, "HORIZONTAL", block)
                elif (
                    self.y == bb
                    and block.x < self.x < br
                    and "UP" in self.direction
                ):
                    turn_laser(self, "VERTICAL", block)
                elif (
                    self.y == block.y
                    and block.x < self.x < br
                    and "DOWN" in self.direction
                ):
                    turn_laser(self, "VERTICAL", block)
                # 隅に当たった場合の処理
                elif self.x in (block.x, br) and self.y in (block.y, bb):
                    collided_blocks_by_corner.append(block)
            if collided_blocks_by_corner:
                if len(collided_blocks_by_corner) == 3:
                    turn_laser(self,"BOTH", collided_blocks_by_corner[0])
                elif len(collided_blocks_by_corner) == 1:
                    block = collided_blocks_by_corner[0]
                    if "RIGHT" in self.direction:
                        next_x = self.x + 1
                    else:
                        next_x = self.x - 1
                    if "DOWN" in self.direction:
                        next_y = self.y + 1
                    else:
                        next_y = self.y - 1
                    if (block.x < next_x < block.x + block.width
                    and block.y < next_y < block.y + block.height):
                        turn_laser(self, "BOTH", block)
                elif collided_blocks_by_corner[0].x == collided_blocks_by_corner[1].x:
                    turn_laser(self, "HORIZONTAL", collided_blocks_by_corner[0])
                elif collided_blocks_by_corner[0].y == collided_blocks_by_corner[1].y:
                    turn_laser(self, "VERTICAL", collided_blocks_by_corner[0])

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


def turn_laser(self, direction, block):
    old_dir = self.direction
    if direction == "HORIZONTAL":
        if self.direction == "UP_RIGHT":
            self.direction = "UP_LEFT"
        elif self.direction == "UP_LEFT":
            self.direction = "UP_RIGHT"
        elif self.direction == "DOWN_RIGHT":
            self.direction = "DOWN_LEFT"
        elif self.direction == "DOWN_LEFT":
            self.direction = "DOWN_RIGHT"
        self.x = block.x - 1 if "LEFT" in self.direction else block.x + block.width + 1
        self.y = self.y - 1 if "UP" in self.direction else self.y + 1
    elif direction == "VERTICAL":
        if self.direction == "UP_RIGHT":
            self.direction = "DOWN_RIGHT"
        elif self.direction == "UP_LEFT":
            self.direction = "DOWN_LEFT"
        elif self.direction == "DOWN_RIGHT":
            self.direction = "UP_RIGHT"
        elif self.direction == "DOWN_LEFT":
            self.direction = "UP_LEFT"
        self.x = self.x - 1 if "LEFT" in self.direction else self.x + 1
        self.y = block.y - 1 if "UP" in self.direction else block.y + block.height + 1
    elif direction == "BOTH":
        if self.direction == "UP_RIGHT":
            self.direction = "DOWN_LEFT"
        elif self.direction == "UP_LEFT":
            self.direction = "DOWN_RIGHT"
        elif self.direction == "DOWN_RIGHT":
            self.direction = "UP_LEFT"
        elif self.direction == "DOWN_LEFT":
            self.direction = "UP_RIGHT"
        self.x = self.x - 1 if "LEFT" in self.direction else self.x + 1
        self.y = block.y - 1 if "UP" in self.direction else block.y + block.height + 1

    spawn_particles(self.particles, self.x, self.y,
                    direction_to_angle(old_dir, self.direction), 9,
                    count=10, spread=math.pi/4)