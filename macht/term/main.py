import sys
import random
import signal
import argparse
from functools import partial, reduce
from itertools import chain

import blessed

from .. import save
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
        return {'rows': int(rows), 'cols': int(cols)}
    except ValueError:
        raise argparse.ArgumentTypeError(
            "grid dimension should look like: '4x4'")


parser = argparse.ArgumentParser(
    description="A game with the objective of merging tiles by moving them.",
    epilog="Use the arrow, wasd or hjkl keys to move the tiles.")
parser.add_argument('grid_dims', metavar='GRID_DIMENSIONS',
                    type=grid_dimension, nargs='*',
                    help="Dimensions used for grid(s), default: '4x4'")
parser.add_argument('-b', '--base', metavar='N', type=int,
                    help="base value of all tiles")
parser.add_argument('-r', '--resume', metavar='SAVE_FILE', nargs='?',
                    default=False, const=None,
                    help="resume previous game. SAVE_FILE is used to save to "
                    "and resume from. Specifying grid dimensions and/or base "
                    "starts a new game without resuming from SAVE_FILE.")


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

        grid.draw()
        grid.update_tiles()
        grid.draw_tiles()

    return True


def main(args=None):
    global do_resize
    do_resize = True

    term = blessed.Terminal()
    term_too_small = False
    game_over = False

    def on_resize(signal, frame):
        global do_resize
        do_resize = True
    signal.signal(signal.SIGWINCH, on_resize)

    opts = parser.parse_args(args or sys.argv[1:])
    grid_dims = opts.grid_dims or [{'rows': 4, 'cols': 4}]
    base_num = opts.base or 2
    resume = opts.resume if opts.resume is not False else False

    grids = []
    save_state = {}
    if resume is not False and not (opts.grid_dims or opts.base):
        save_state = save.load_from_file(resume)

    score = save_state.get('score', 0)
    for grid_state in save_state.get('grids', grid_dims):
        TermTile = partial(Tile, term=term,
                           base=grid_state.pop('base', base_num))
        tiles = grid_state.pop('tiles', ())

        grid = Grid(x=0, y=1, term=term, Tile=TermTile, **grid_state)
        if tiles:
            for tile_state in tiles:
                grid.spawn_tile(**tile_state)
        else:
            grid.spawn_tile()
            grid.spawn_tile()

        game_over = game_over or len(grid.possible_moves) == 0

        grids.append(grid)

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            if do_resize:
                term_too_small = not term_resize(term, grids)
                do_resize = False

            if not term_too_small:
                draw_score(score, term, end=game_over)

            key = term.inkey(_intr_continue=False)
            if key in ('q', 'KEY_ESCAPE') or game_over:
                save.write_to_file(score, grids, filename=resume or None)
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
                    game_over = game_over or len(grid.possible_moves) == 0

    high = 0
    for max_tile in filter(None, (g.highest_tile for g in grids)):
        high = max(high, max_tile.value)
    print("highest tile: {}\nscore: {}".format(high, score))

    return 0
