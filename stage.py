from block import Block
from can_be_laser_potion import CanBeLaserPotion
from flag_block import FlagBlock
from gate import Gate
from config import GRID_SIZE
from death_block import DeathBlock
from coin import Coin
from save_point import SavePoint


class Stage:
    def __init__(self, ascii_map, index_x, index_y, block_size=GRID_SIZE):
        self.collidables = []
        self.coins = []
        self.can_be_laser_potions = []
        self.block_size = block_size
        self.start_position = None
        self.map = ascii_map
        self.index_x = index_x
        self.index_y = index_y
        self.parse_ascii_map(ascii_map)

    def parse_ascii_map(self, ascii_map):
        absorbing_blocks = []
        for y, line in enumerate(ascii_map):
            for x, char in enumerate(line):
                block_x = x * self.block_size
                block_y = y * self.block_size
                if char == "S":
                    self.collidables.append(SavePoint(
                        self.index_x,
                        self.index_y,
                        block_x,
                        block_y,
                    ))
                elif char == "#":
                    self.collidables.append(
                        Block(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            collide_with_player=True,
                            collide_with_laser="ABSORB",
                        )
                    )
                elif char == "M":  # ミラー
                    self.collidables.append(
                        Block(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            collide_with_player=True,
                            collide_with_laser="REFLECT",
                        )
                    )
                elif char == "g":  # ガラス
                    self.collidables.append(
                        Block(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            collide_with_player=True,
                            collide_with_laser="TRANSPARENT",
                        )
                    )
                elif char == "B":  # 黒
                    self.collidables.append(
                        Block(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            collide_with_player=False,
                            collide_with_laser="ABSORB",
                        )
                    )
                elif char == "W":  # 水
                    self.collidables.append(
                        Block(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            collide_with_player=False,
                            collide_with_laser="REFLECT",
                        )
                    )
                elif char == "D":
                    self.collidables.append(
                        DeathBlock(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            self.start_position,
                            collide_with_player=True,
                            collide_with_laser="ABSORB",
                        )
                    )
                elif char in "v^<>":
                    if char == "v":
                        absorbing_block = FlagBlock(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            absorb_side="BOTTOM",
                            collide_with_laser="ABSORB",
                        )
                    elif char == "^":
                        absorbing_block = FlagBlock(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            absorb_side="TOP",
                            collide_with_laser="ABSORB",
                        )
                    elif char == "<":
                        absorbing_block = FlagBlock(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            absorb_side="LEFT",
                            collide_with_laser="ABSORB",
                        )
                    elif char == ">":
                        absorbing_block = FlagBlock(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            absorb_side="RIGHT",
                            collide_with_laser="ABSORB",
                        )
                    self.collidables.append(absorbing_block)
                    absorbing_blocks.append(absorbing_block)
                elif char == "X":
                    self.collidables.append(
                        Gate(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            collidable_with_player=True,
                            collide_with_laser="ABSORB",
                            linked_absorbing_blocks=absorbing_blocks,
                        )
                    )
                elif char == "Y":
                    self.collidables.append(
                        Gate(
                            block_x,
                            block_y,
                            self.block_size,
                            self.block_size,
                            collidable_with_player=True,
                            collide_with_laser="ABSORB",
                            linked_absorbing_blocks=absorbing_blocks,
                            initial_exist=False,
                        )
                    )
                elif char == "C":
                    self.coins.append(
                        Coin(
                            block_x,
                            block_y
                        )
                    
                    )
                elif char == "P":
                    self.can_be_laser_potions.append(
                        CanBeLaserPotion(
                            block_x,
                            block_y
                        )
                    )
                    

    def update(self):
        for collidable in self.collidables:
            collidable.update()

    def reset(self):
        self.__init__(self.map, self.index_x, self.index_y)

    def draw(self, offset_x=0, offset_y=0):
        for collidable in self.collidables:
            collidable.draw(offset_x, offset_y)
        for coin in self.coins:
            coin.draw(offset_x, offset_y)
        for can_be_laser_potion in self.can_be_laser_potions:
            can_be_laser_potion.draw(offset_x, offset_y)
        