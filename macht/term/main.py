import sys
import random
import signal
import argparse
from functools import partial, reduce
from itertools import chain
from collections import namedtuple

import blessed

from ..grid import Direction, Actions
from .grid import Grid
from .tile import Tile

TileDimensions = namedtuple('TileDimensions', "width height")

up, left = ('w', 'k', 'KEY_UP'), ('a', 'h', 'KEY_LEFT')
down, right = ('s', 'j', 'KEY_DOWN'), ('d', 'l', 'KEY_RIGHT')

grid_moves = {}
for keys, direction in zip((up, left, down, right), Direction):
    grid_moves.update(dict.fromkeys(keys, direction))


def grid_dimension(string):
    rows, _, cols = string.partition('x')
    try:
        return int(rows), int(cols)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "grid dimension was should look like: '4x4'")


parser = argparse.ArgumentParser(
    description="A game with the objective of merging tiles by moving them.",
    epilog="Use the arrow, wasd or hjkl keys to move the tiles.")
parser.add_argument('grid_dims', metavar='GRID_DIMENSIONS', default=[(4, 4)],
                    type=grid_dimension, nargs='*',
                    help="Dimensions used for grid(s), default: '4x4'")
parser.add_argument('-b', '--base', metavar='N', dest='base', type=int,
                    default=2, help="base value of all tiles")


def draw_score(score, term, end=False):
    msg = "score: " + str(score)
    with term.location(term.width // 2 - len(msg) // 2, 0):
        print(term.bold_on_red(msg) if end else term.bold(msg))


def term_resize(term, grids, signum=None, frame=None):
    print(term.clear())

    max_width = (term.width - (len(grids) + 1) * 2) // len(grids)

    for grid in grids:
        for tile_height in range(10, 2, -1):
            grid.tile_height, grid.tile_width = tile_height, tile_height * 2

            if grid.height + 1 < term.height and grid.width <= max_width:
                break
        else:
            with term.location(0, 0):
                print(term.red("terminal size is too small;\n"
                               "please resize the terminal"))

            return

    margin = (term.width - sum(g.width for g in grids) -
              (len(grids) - 1) * 2) // 2
    for grid_idx, grid in enumerate(grids):
        grid.x = margin + sum(g.width for g in grids[:grid_idx]) + grid_idx * 2

        for row_idx, row in enumerate(grid):
            for col_idx, tile in enumerate(row):
                if tile:
                    tile.x, tile.y = grid.tile_coord(row_idx, col_idx)
                    tile.height, tile.width = grid.tile_height, grid.tile_width

                    grid[row_idx][col_idx] = tile

        grid.draw()
        grid.draw_tiles()


def main(args=None):
    opts = parser.parse_args(args or sys.argv[1:])

    term = blessed.Terminal()

    DimTile = partial(Tile, base=opts.base, term=term)

    grids = []
    for grid_dim in opts.grid_dims:
        rows, cols = grid_dim

        grid = Grid(x=0, y=1, rows=rows, cols=cols, term=term, Tile=DimTile)
        grid.spawn_tile()
        grid.spawn_tile()

        grids.append(grid)

    signal.signal(signal.SIGWINCH, partial(term_resize, term, grids))

    score = 0
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        term_resize(term, grids)

        key = blessed.keyboard.Keystroke('')
        game_over = False
        while key != 'q' and not game_over:
            draw_score(score, term)

            key = term.inkey()

            direction = grid_moves.get(key.name or key)
            if direction:
                for grid in grids:
                    actions = grid.move(direction)

                    for action in actions:
                        grid.draw_empty_tile(*action.old)

                        if action.type == Actions.merge:
                            row, column = action.new
                            score += grid[row][column].value

                    if actions:  # had a successfull move?
                        grid.spawn_tile(
                            exponent=2 if random.random() > 0.9 else 1)

                        grid.draw_tiles()

                    if all(chain(*grid)):
                        possible_moves = 0
                        for direction in Direction:
                            if grid.move(direction, apply=False):
                                possible_moves += 1

                        if possible_moves == 0:
                            draw_score(score, term, end=True)
                            term.inkey()

                            game_over = True

    high = reduce(lambda o, t: max(o, t.value),
                  filter(None, chain(t for g in grids for t in chain(*g))), 0)
    print("highest tile: {}\nscore: {}".format(high, score))

    return 0
