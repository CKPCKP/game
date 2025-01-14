from block import Block
from absorbing_block import AbsorbingBlock
from gate import Gate

class Stage:
    def __init__(self, ascii_map, block_size=8):
        self.blocks = []
        self.gates = []
        self.block_size = block_size
        self.parse_ascii_map(ascii_map)

    def parse_ascii_map(self, ascii_map):
        absorbing_blocks = []
        for y, line in enumerate(ascii_map):
            for x, char in enumerate(line):
                block_x = x * self.block_size
                block_y = y * self.block_size
                if char == '#':  # '#'を通常のブロックとして扱う
                    self.blocks.append(Block(block_x, block_y, self.block_size, self.block_size))
                elif char in 'v^<>':
                    if char == 'v':
                        absorbing_block = AbsorbingBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='BOTTOM')
                    elif char == '^':
                        absorbing_block = AbsorbingBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='TOP')
                    elif char == '<':
                        absorbing_block = AbsorbingBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='LEFT')
                    elif char == '>':
                        absorbing_block = AbsorbingBlock(block_x, block_y, self.block_size, self.block_size, absorb_side='RIGHT')
                    self.blocks.append(absorbing_block)
                    absorbing_blocks.append(absorbing_block)
                elif char == 'G':  # 'G'をゲートとして扱う
                    self.gates.append(Gate(block_x, block_y, self.block_size, self.block_size, absorbing_blocks))

    def update(self, player):
        for block in self.blocks:
            block.update()
            block.check_collision(player)
        for gate in self.gates:
            gate.update()
            gate.check_collision(player)

    def draw(self):
        for block in self.blocks:
            block.draw()
        for gate in self.gates:
            gate.draw()
