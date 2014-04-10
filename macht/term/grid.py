from itertools import product, chain

from .. import grid
from . import tile

bg_colors = ['red', 'magenta', 'green', 'cyan', 'blue', 'cyan', 'yellow']
fg_colors = ['black', 'black', 'black', 'black', 'white', 'black', 'black']


class Grid(grid.Grid):
    vert_div = '||'
    hor_div = '='
    cross_div = 'XX'

    def __init__(self, x=0, y=0, rows=0, cols=0, tile_width=0, tile_height=0,
                 term=None, Tile=tile.Tile):
        super(Grid, self).__init__(rows=rows, cols=cols, Tile=Tile)
        self.x, self.y = x, y
        self.tile_width, self.tile_height = tile_width, tile_height
        self.term = term

    def draw(self, fg='white', bg=None):
        style = getattr(self.term, fg + ("_on_" + bg if bg else ""))
        rows, cols = len(self), len(self[0])

        for col_idx in range(cols - 1):
            hor_offset = ((col_idx + 1) * self.tile_width +
                          col_idx * len(self.vert_div))

            for vert_offset in range(self.height):
                with self.term.location(self.x + hor_offset,
                                        self.y + vert_offset):
                    print(style(self.vert_div))

        for row_idx in range(rows - 1):
            vert_offset = (row_idx + 1) * self.tile_height + row_idx
            with self.term.location(self.x, self.y + vert_offset):
                print(style(self.cross_div.join(
                      [self.hor_div * self.tile_width] * cols)))

    def update_tiles(self):
        for row_idx, col_idx in product(range(len(self)), range(len(self[0]))):
            if self[row_idx][col_idx]:
                tile = self[row_idx][col_idx]
                tile.x, tile.y = self.tile_coord(row_idx, col_idx)
                tile.height, tile.width = self.tile_height, self.tile_width
                self[row_idx][col_idx] = tile

    def draw_tiles(self):
        for tile in filter(None, chain(*self)):  # all non-empty tiles
            # choose a color, use modulo to support any value of a tile
            # all bg colors have a bright variant doubling the amount of colors
            color_idx = (tile.exponent - 1) % (len(bg_colors) * 2) // 2
            bg = bg_colors[color_idx]
            if self.term.number_of_colors >= 16 and tile.exponent % 2 == 0:
                bg = "bright_" + bg

            tile.draw(fg=fg_colors[color_idx], bg=bg)

    def draw_empty_tile(self, row, column):
        x, y = self.tile_coord(row, column)
        for y_offset in range(self.tile_height):
            with self.term.location(x, y + y_offset):
                print(' ' * self.tile_width)

    @property
    def width(self):
        cols = len(self[0])
        if cols > 0:
            return cols * self.tile_width + (cols - 1) * len(self.vert_div)
        return 0

    @property
    def height(self):
        rows = len(self)
        if rows > 0:
            return rows * self.tile_height + rows - 1
        return 0

    def tile_coord(self, row, column):
        if row >= len(self) or column >= len(self[0]):
            raise IndexError

        x = self.x + column * self.tile_width + column * len(self.vert_div)
        y = self.y + row * self.tile_height + row

        return x, y

    def spawn_tile(self, *args, **kwargs):
        action = super(Grid, self).spawn_tile(*args, **kwargs)
        row, column = action.new

        if kwargs.get('apply', True):
            x, y = self.tile_coord(row, column)
            self[row][column].x, self[row][column].y = x, y
            self[row][column].height = self.tile_height
            self[row][column].width = self.tile_width

        return action

    def move(self, *args, **kwargs):
        actions = super(Grid, self).move(*args, **kwargs)

        if kwargs.get('apply', True):
            for action in actions:
                row, col = action.new

                self[row][col].x, self[row][col].y = self.tile_coord(row, col)

        return actions
