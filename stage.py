from block import Block
from absorbing_block import AbsorbingBlock
from gate import Gate
from config import GRID_SIZE
from death_block import DeathBlock

class Stage:
    def __init__(self, ascii_map, block_size=GRID_SIZE):
        self.collidables = []
        self.block_size = block_size
        self.parse_ascii_map(ascii_map)

    def parse_ascii_map(self, ascii_map):
        absorbing_blocks = []
        for y, line in enumerate(ascii_map):
            for x, char in enumerate(line):
                block_x = x * self.block_size
                block_y = y * self.block_size
                if char == '#':
                    self.collidables.append(Block(block_x, block_y, self.block_size, self.block_size))
                elif char == 'D':
                    self.collidables.append(DeathBlock(block_x, block_y, self.block_size, self.block_size))
                elif char in 'v^<>':
                    if char == 'v':
                        absorbing_block = AbsorbingBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='BOTTOM')
                    elif char == '^':
                        absorbing_block = AbsorbingBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='TOP')
                    elif char == '<':
                        absorbing_block = AbsorbingBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='LEFT')
                    elif char == '>':
                        absorbing_block = AbsorbingBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='RIGHT')
                    self.collidables.append(absorbing_block)
                    absorbing_blocks.append(absorbing_block)
                elif char == 'G':  # 'G'をゲートとして扱う
                    self.collidables.append(Gate(block_x, block_y, self.block_size, self.block_size, absorbing_blocks))

    def update(self, player):
        for collidable in self.collidables:
            collidable.update()
            collidable.check_collision(player)

    def draw(self):
        for collidable in self.collidables:
            collidable.draw()
