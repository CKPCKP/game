from block import Block

class Stage:
    def __init__(self, ascii_map, block_size=8):
        self.blocks = []
        self.block_size = block_size
        self.parse_ascii_map(ascii_map)

    def parse_ascii_map(self, ascii_map):
        for y, line in enumerate(ascii_map):
            for x, char in enumerate(line):
                if char == '#':  # '#'をブロックとして扱う
                    block_x = x * self.block_size
                    block_y = y * self.block_size
                    self.blocks.append(Block(block_x, block_y, self.block_size, self.block_size))

    def update(self, player):
        for block in self.blocks:
            block.update()
            block.check_collision(player)

    def draw(self):
        for block in self.blocks:
            block.draw()
