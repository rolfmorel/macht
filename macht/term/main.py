import sys
import random
import signal
import argparse
from functools import partial
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

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--columns', metavar='N', dest='columns',
                    type=int, default=4)
parser.add_argument('-r', '--rows', metavar='N', dest='rows', type=int,
                    default=4)
parser.add_argument('-b', '--base', metavar='N', dest='base', type=int,
                    default=2)


def draw_score(score, grid, term, end=False):
    msg = "score: " + str(score)
    with term.location(grid.x + grid.width - len(msg), 0):
        print(term.bold_on_red(msg) if end else term.bold(msg))


def term_resize(term, grid, signum, frame):
    print(term.clear())
    grid.x = term.width // 2 - grid.width // 2

    for row_idx, row in enumerate(grid):
        for col_idx, tile in enumerate(row):
            if tile:
                tile.x, tile.y = grid.tile_coord(row_idx, col_idx)
                grid[row_idx][col_idx] = tile

    grid.draw()
    grid.draw_tiles()


def main(args=None):
    opts = parser.parse_args(args or sys.argv[1:])

    term = blessed.Terminal()

    tile_dim = TileDimensions(10, 5)

    DimTile = partial(Tile, base=opts.base, width=tile_dim.width,
                      height=tile_dim.height, term=term)

    grid = Grid(x=0, y=1, rows=opts.rows, cols=opts.columns,
                tile_width=tile_dim.width, tile_height=tile_dim.height,
                term=term, Tile=DimTile)
    grid.x = term.width // 2 - grid.width // 2

    signal.signal(signal.SIGWINCH, partial(term_resize, term, grid))

    grid.spawn_tile()
    grid.spawn_tile()

    score = 0
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        grid.draw()
        grid.draw_tiles()

        key = blessed.keyboard.Keystroke('')
        while key != 'q':
            draw_score(score, grid, term)

            try:  # the signal handler for SIGWINCH might be called
                key = term.inkey()
            except InterruptedError:
                key = blessed.keyboard.Keystroke('')

            direction = grid_moves.get(key.name or key)
            if direction:
                actions = grid.move(direction)

                for action in actions:
                    grid.draw_empty_tile(*action.old)

                    if action.action == Actions.merge:
                        score += grid[action.new.row][action.new.column].value

                if actions:  # had a successfull move?
                    grid.spawn_tile(exponent=2 if random.random() > 0.9 else 1)

                    grid.draw_tiles()

                if not list(filter(lambda t: not t, chain(*grid))):  # full?
                    possible_moves = 0
                    for direction in Direction:
                        if grid.move(direction, apply=False):
                            possible_moves += 1

                    if possible_moves == 0:
                        draw_score(score, grid, term, end=True)
                        term.inkey()

                        return 2

    return 0
