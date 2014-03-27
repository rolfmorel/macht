import sys
import random
import signal
import argparse
from functools import partial, reduce
from itertools import chain

import blessed

from ..grid import Direction, Actions
from .grid import Grid
from .tile import Tile

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
            "grid dimension should look like: '4x4'")


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


def term_resize(term, grids):
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
            return False  # game can not continue until after another resize

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

    return True


def main(args=None):
    global do_resize
    do_resize = True

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

    def on_resize(signal, frame):
        global do_resize
        do_resize = True
    signal.signal(signal.SIGWINCH, on_resize)

    score = 0
    game_over = False
    term_too_small = False
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            if do_resize:
                term_too_small = not term_resize(term, grids)
                do_resize = False

            if not term_too_small:
                draw_score(score, term, end=game_over)

            key = term.inkey(0.5)
            if key == 'q' or game_over:
                break

            direction = grid_moves.get(key.name or key)
            if not direction or term_too_small:
                continue

            for grid in grids:
                actions = grid.move(direction)

                for action in actions:
                    grid.draw_empty_tile(*action.old)

                    if action.type == Actions.merge:
                        row, column = action.new
                        score += grid[row][column].value

                if actions:  # had any successfull move(s)?
                    grid.spawn_tile(exponent=2 if random.random() > 0.9 else 1)

                    grid.draw_tiles()

                if all(chain(*grid)):
                    for dir in Direction:
                        if grid.move(dir, apply=False):
                            break  # At least one possible move
                    else:  # No possible moves
                        game_over = True

    high = reduce(lambda o, t: max(o, t.value),
                  filter(None, chain(t for g in grids for t in chain(*g))), 0)
    print("highest tile: {}\nscore: {}".format(high, score))

    return 0
