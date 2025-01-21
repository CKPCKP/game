from block import Block
from flag_block import FlagBlock
from gate import Gate
from config import GRID_SIZE
from death_block import DeathBlock

class Stage:
    def __init__(self, ascii_map, block_size=GRID_SIZE):
        self.collidables = []
        self.block_size = block_size
        self.parse_ascii_map(ascii_map)
        self.start_position = None

    def parse_ascii_map(self, ascii_map):
        absorbing_blocks = []
        for y, line in enumerate(ascii_map):
            for x, char in enumerate(line):
                block_x = x * self.block_size
                block_y = y * self.block_size
                if char == 'S':
                    self.start_position = (block_x, block_y)
                elif char == '#':
                    self.collidables.append(Block(block_x, block_y, self.block_size, self.block_size, collide_with_player=True, collide_with_laser="ABSORB"))
                elif char == 'M': # ミラー
                    self.collidables.append(Block(block_x, block_y, self.block_size, self.block_size, collide_with_player=True, collide_with_laser="REFLECT"))
                elif char == 'g': # ガラス
                    self.collidables.append(Block(block_x, block_y, self.block_size, self.block_size, collide_with_player=True, collide_with_laser="TRANSPARENT"))
                elif char == 'B': # 黒
                    self.collidables.append(Block(block_x, block_y, self.block_size, self.block_size, collide_with_player=False, collide_with_laser="ABSORB"))
                elif char == 'D':
                    self.collidables.append(DeathBlock(block_x, block_y, self.block_size, self.block_size, self.start_position, collide_with_player=True, collide_with_laser="ABSORB"))
                elif char in 'v^<>':
                    if char == 'v':
                        absorbing_block = FlagBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='BOTTOM', collide_with_laser="ABSORB")
                    elif char == '^':
                        absorbing_block = FlagBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='TOP', collide_with_laser="ABSORB")
                    elif char == '<':
                        absorbing_block = FlagBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='LEFT', collide_with_laser="ABSORB")
                    elif char == '>':
                        absorbing_block = FlagBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='RIGHT', collide_with_laser="ABSORB")
                    self.collidables.append(absorbing_block)
                    absorbing_blocks.append(absorbing_block)
                elif char == 'G':  # 'G'をゲートとして扱う
                    self.collidables.append(Gate(block_x, block_y, self.block_size, self.block_size, collidable_with_player=True, collide_with_laser="ABSORB", linked_absorbing_blocks=absorbing_blocks))

    def update(self):
        for collidable in self.collidables:
            collidable.update()

    def draw(self):
        for collidable in self.collidables:
            collidable.draw()
