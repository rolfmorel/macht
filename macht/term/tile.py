from .. import tile


class Tile(tile.Tile):
    def __init__(self, base=2, exponent=1, x=0, y=0, width=0, height=0,
                 term=None):
        super(Tile, self).__init__(base=base, exponent=exponent)
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.term = term

    def draw(self, text=None, fg='white', bg='black'):
        text = text or str(self.value)
        style = getattr(self.term, fg + ("_on_" + bg if bg else ""))

        for y_offset in range(self.height):
            with self.term.location(self.x, self.y + y_offset):
                print(style(' ' * self.width))

        hor_offset = (self.width + 1) // 2 - (len(text) + 1) // 2
        vert_offset = (self.height + 1) // 2 - 1
        with self.term.location(self.x + hor_offset, self.y + vert_offset):
            print(style(text))
