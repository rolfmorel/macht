from itertools import product, chain

import pytest
from macht import grid


def test_init():
    g = grid.Grid()
    assert len(g) == len(g._grid) == 4
    assert len(g[0]) == len(g._grid[0]) == 4

    g = grid.Grid(rows=1, cols=1)
    assert len(g) == 1 and len(g[0]) == 1

    g = grid.Grid(rows=8, cols=3)
    assert len(g) == 8 and len(g[0]) == 3


def test_spawn_tile():
    def new_grid(rows, cols, spawn):
        g = grid.Grid(rows, cols)
        for _ in range(spawn):
            g.spawn_tile()

        return g

    assert sum(1 for _ in filter(None, chain(*new_grid(4, 4, 1)))) == 1
    assert sum(1 for _ in filter(None, chain(*new_grid(4, 4, 4)))) == 4

    assert sum(1 for _ in filter(None, chain(*new_grid(2, 2, 4)))) == 4
    assert sum(1 for _ in filter(None, chain(*new_grid(6, 6, 4)))) == 4

    assert sum(1 for _ in filter(None, chain(*new_grid(6, 6, 18)))) == 18

    pytest.raises(grid.SpawnTileError, new_grid, 4, 4, 17)

    g = grid.Grid()
    g.spawn_tile(row=0, column=0)
    assert g[0][0]

    pytest.raises(grid.SpawnTileError, g.spawn_tile, row=0, column=0)

    g.spawn_tile(row=0)
    g.spawn_tile(row=0)
    g.spawn_tile(row=0)
    assert all(g[0])
    pytest.raises(grid.SpawnTileError, g.spawn_tile, row=0)

    g.spawn_tile(column=0)
    g.spawn_tile(column=0)
    g.spawn_tile(column=0)
    assert all(g[row_idx][0] for row_idx in range(4))
    pytest.raises(grid.SpawnTileError, g.spawn_tile, column=0)

    action = g.spawn_tile(3, 3)
    assert g[3][3]
    assert action.type is grid.Actions.spawn and action.new == (3, 3)

    action = g.spawn_tile(1, 2, apply=False)
    assert not g[1][2]
    assert action.type is grid.Actions.spawn and action.new == (1, 2)

    g.spawn_tile(2, 1, base=3, exponent=4)
    assert g[2][1].base == 3 and g[2][1].exponent == 4


def test_highest_tile():
    g = grid.Grid()
    assert g.highest_tile is None

    g.spawn_tile(exponent=1)
    assert g.highest_tile
    g.spawn_tile(exponent=2)
    assert g.highest_tile.exponent == 2


def test_possible_moves():
    g = grid.Grid()
    assert len(g.possible_moves) == 0

    g.spawn_tile(1, 0)
    assert len(g.possible_moves) == 3

    g.move(grid.Direction.up)
    assert g.possible_moves == [grid.Direction.down, grid.Direction.right]

    g.spawn_tile(1, 0, exponent=2)
    assert len(g.possible_moves) == 2

    g.spawn_tile(2, 0, exponent=1)
    g.spawn_tile(3, 0, exponent=2)
    assert g.possible_moves == [grid.Direction.right]

    exponent = 2
    for row_idx, col_idx in product(range(len(g)), range(1, len(g[0]))):
        g.spawn_tile(row_idx, col_idx, exponent=exponent)
        exponent += 1
    assert len(g.possible_moves) == 0


def test_resize():
    g = grid.Grid()

    g.resize(rows=6, cols=6)
    assert len(g) == 6 and len(g[0]) == 6

    g.spawn_tile(0, 0)
    g.spawn_tile(3, 3)
    g.spawn_tile(5, 5)
    assert sum(1 for _ in filter(None, chain(*g))) == 3

    g.resize(rows=4)
    assert len(g) == 4 and sum(1 for _ in filter(None, chain(*g))) == 2

    g.resize(cols=2)
    assert len(g[0]) == 2 and sum(1 for _ in filter(None, chain(*g))) == 1


def test_move_tile_merge_tiles():
    g = grid.Grid()
    g.spawn_tile(0, 0)
    g.move_tile(grid.Position(0, 0), grid.Position(0, 3))
    g.move_tile((0, 3), (3, 3))
    assert g[3][3] and not g[0][0] and not g[0][3]

    action = g.move_tile((3, 3), (3, 0), apply=False)
    assert action.type == grid.Actions.move
    assert action.old == (3, 3) and action.new == (3, 0)

    pytest.raises(ValueError, g.merge_tiles, grid.Position(3, 3), (0, 3))
    pytest.raises(ValueError, g.merge_tiles, (0, 3), grid.Position(3, 3))

    g.spawn_tile(2, 3)

    action = g.merge_tiles((2, 3), (3, 3), apply=False)
    assert action.type is grid.Actions.merge
    assert action.old == (2, 3) and action.new == (3, 3)
    assert g[2][3] and g[3][3]

    g.merge_tiles((2, 3), (3, 3))

    assert g[3][3] and not g[2][3] and g[3][3].exponent == 2


def test_move():
    g = grid.Grid()
    g.spawn_tile(0, 0)
    g.spawn_tile(3, 0)

    pytest.raises(TypeError, g.move, "right")

    actions = g.move(grid.Direction.right)
    assert len(actions) == 2
    assert all(action.type is grid.Actions.move for action in actions)
    assert actions[0].old == (0, 0) and actions[0].new == (0, 3)
    assert actions[1].old == (3, 0) and actions[1].new == (3, 3)

    actions = g.move(grid.Direction.left)
    assert actions[0].old == (0, 3) and actions[0].new == (0, 0)
    assert actions[1].old == (3, 3) and actions[1].new == (3, 0)

    g = grid.Grid()
    g.spawn_tile(0, 1)
    g.spawn_tile(0, 2)

    actions = g.move(grid.Direction.down)
    assert all(action.type is grid.Actions.move for action in actions)
    assert actions[0].old == (0, 1) and actions[0].new == (3, 1)
    assert actions[1].old == (0, 2) and actions[1].new == (3, 2)

    g = grid.Grid()
    g.spawn_tile(1, 1)
    g.spawn_tile(2, 2)

    actions = g.move(grid.Direction.up)
    assert actions[0].old == (1, 1) and actions[0].new == (0, 1)
    assert actions[1].old == (2, 2) and actions[1].new == (0, 2)

    g.spawn_tile(1, 1, exponent=2)
    actions = g.move(grid.Direction.down)
    assert actions[0].old == (1, 1) and actions[0].new == (3, 1)
    assert actions[1].old == (0, 1) and actions[1].new == (2, 1)
    assert actions[2].old == (0, 2) and actions[2].new == (3, 2)


def test_move_merge():
    g = grid.Grid()
    g.spawn_tile(0, 0)
    g.spawn_tile(0, 3)

    actions = g.move(grid.Direction.right)
    assert actions[0].type is grid.Actions.merge
    assert actions[0].old == (0, 0) and actions[0].new == (0, 3)
    assert g[actions[0].new.row][actions[0].new.column].exponent == 2
    assert sum(1 for _ in filter(None, chain(*g))) == 1

    g.spawn_tile(2, 3, exponent=2)
    actions = g.move(grid.Direction.down)
    assert actions[0].type is grid.Actions.move
    assert actions[1].type is grid.Actions.merge
    assert g[actions[1].new.row][actions[1].new.column].exponent == 3

    g.spawn_tile(3, 0, exponent=3)
    g.spawn_tile(3, 1, exponent=3)
    g.spawn_tile(3, 2, exponent=3)
    actions = g.move(grid.Direction.left)
    assert actions[0].type is grid.Actions.merge
    assert actions[1].type is grid.Actions.move
    assert actions[2].type is grid.Actions.merge
    assert g[actions[0].new.row][actions[0].new.column].exponent == 4
    assert sum(1 for _ in filter(None, chain(*g))) == 2

    g.spawn_tile(0, 0)
    g.spawn_tile(2, 0, exponent=4)
    g.spawn_tile(0, 1, exponent=4)
    actions = g.move(grid.Direction.up)
    assert actions[0].type is grid.Actions.move
    assert actions[1].type is grid.Actions.merge
    assert actions[2].type is grid.Actions.merge
    assert g[actions[1].new.row][actions[1].new.column].exponent == 5
    assert sum(1 for _ in filter(None, chain(*g))) == 3


def test_no_merge_after_move():
    "Tiles should not merge when there is another valued tile in between."
    g = grid.Grid()
    g.spawn_tile(0, 0, exponent=1)
    g.spawn_tile(1, 0, exponent=2)
    g.spawn_tile(2, 0, exponent=1)
    g.move(grid.Direction.down)
    assert g[1][0].exponent == 1
    assert g[2][0].exponent == 2
    assert g[3][0].exponent == 1

    g = grid.Grid()
    g.spawn_tile(0, 0, exponent=1)
    g.spawn_tile(0, 1, exponent=2)
    g.spawn_tile(0, 2, exponent=1)
    g.move(grid.Direction.right)
    assert g[0][1].exponent == 1
    assert g[0][2].exponent == 2
    assert g[0][3].exponent == 1


def test_setitem():  # highly impractical, but add for coverage
    g = grid.Grid()
    g[0] = [None for _ in range(len(g[0]))]

    assert g._grid[0] == [None for _ in range(len(g[0]))]


def test_repr():
    from macht.grid import Grid, GridAction, Actions, Position

    assert repr(grid.Grid()) == 'Grid(rows=4, cols=4)'
    eval(repr(grid.Grid()))

    action = grid.GridAction(grid.Actions.spawn,
                             grid.Position(row=3, column=3))
    assert (repr(action) ==
            'GridAction(Actions.spawn, new=Position(row=3, column=3))')
    eval(repr(grid.GridAction(grid.Actions.spawn, grid.Position(3, 3))))
