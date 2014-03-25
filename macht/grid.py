import random
from collections import namedtuple

from enum import Enum

from .tile import Tile

Direction = Enum('Direction', "up left down right")

Position = namedtuple('Position', "row column")

Actions = Enum('Actions', "spawn move merge")


class GridFullError(Exception):
    pass


class GridAction(object):
    def __init__(self, type, new, old=None):
        # Actions:
        self.type = type
        # Position:
        self.new, self.old = new, old

    def __repr__(self):
        return "GridAction({}, new={}{})".format(self.type, self.new,
                ", old=" + str(self.old) if self.old else "")


class Grid(object):
    _grid = [[]]

    def __init__(self, rows=4, cols=4, Tile=Tile):
        self._grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.Tile = Tile

    def __getitem__(self, item):
        return self._grid.__getitem__(item)

    def __setitem__(self, item, value):
        return self._grid.__setitem__(item, value)

    def __delitem__(self, item):
        return self._grid.__delitem__(item)

    def __len__(self):
        return len(self._grid)

    def __repr__(self):
        return "Grid(rows={}, cols={})".format(len(self), len(self[0]))

    def spawn_tile(self, row=None, column=None, apply=True, **kwargs):
        rows, cols = len(self), len(self[0])
        empty_tiles = []
        for row_idx in range(row or 0, row + 1 if row is not None else rows):
            for col_idx in range(
                    column or 0, column + 1 if column is not None else cols):
                if not self[row_idx][col_idx]:
                    empty_tiles.append((row_idx, col_idx))

        if len(empty_tiles) == 0:
            raise GridFullError("no empty tiles")

        row, column = random.choice(empty_tiles)

        if apply:
            self[row][column] = self.Tile(**kwargs)

        return GridAction(Actions.spawn, Position(row, column))

    def move_tile(self, old, new, apply=True):
        old, new = Position(*old), Position(*new)

        if apply:
            self[new.row][new.column] = self[old.row][old.column]
            self[old.row][old.column] = None

        return GridAction(Actions.move, new, old)

    def merge_tiles(self, old, new, apply=True):
        old, new = Position(*old), Position(*new)

        if (not self[new.row][new.column] or
                self[new.row][new.column] != self[old.row][old.column]):
            raise ValueError

        if apply:
            self[new.row][new.column].exponent += 1
            self[old.row][old.column] = None

        return GridAction(Actions.merge, new, old)

    def move_vertical(self, direction, apply=True):
        def correct_direction(seq):
            return reversed(seq) if direction is Direction.down else seq

        for col_idx in range(len(self[0])):
            for row_idx in correct_direction(range(len(self))):
                if direction is Direction.down:
                    pos_in_column = range(row_idx - 1, -1, -1)
                else:
                    pos_in_column = range(row_idx + 1, len(self))

                for row_pos in pos_in_column:
                    if self[row_idx][col_idx]:  # Tile occupied, maybe merge
                        if self[row_pos][col_idx]:
                            if self[row_idx][col_idx] == self[row_pos][col_idx]:
                                old = Position(row_pos, col_idx)
                                new = Position(row_idx, col_idx)

                                yield self.merge_tiles(old, new, apply=apply)
                            break
                    elif self[row_pos][col_idx]:
                        old = Position(row_pos, col_idx)
                        new = Position(row_idx, col_idx)

                        yield self.move_tile(old, new, apply=apply)

                        for row_pos in pos_in_column:
                            if self[row_idx][col_idx] == self[row_pos][col_idx]:
                                old = Position(row_pos, col_idx)

                                yield self.merge_tiles(old, new, apply=apply)

                                break
                        break

    def move_horizontal(self, direction, apply=True):
        def correct_direction(seq):
            return reversed(seq) if direction is Direction.right else seq

        for row_idx in range(len(self)):
            for col_idx in correct_direction(range(len(self[0]))):
                if direction is Direction.right:
                    pos_in_row = range(col_idx - 1, -1, -1)
                else:
                    pos_in_row = range(col_idx + 1, len(self[0]))

                for col_pos in pos_in_row:
                    if self[row_idx][col_idx]:
                        if self[row_idx][col_pos]:
                            if self[row_idx][col_idx] == self[row_idx][col_pos]:
                                old = Position(row_idx, col_pos)
                                new = Position(row_idx, col_idx)

                                yield self.merge_tiles(old, new, apply=apply)
                            break
                    elif self[row_idx][col_pos]:
                        old = Position(row_idx, col_pos)
                        new = Position(row_idx, col_idx)

                        yield self.move_tile(old, new, apply=apply)

                        for col_pos in pos_in_row:
                            if self[row_idx][col_idx] == self[row_idx][col_pos]:
                                old = Position(row_idx, col_pos)

                                yield self.merge_tiles(old, new, apply=apply)

                                break
                        break

    def move(self, direction, apply=True):
        if not isinstance(direction, Direction):
            raise TypeError

        if direction in (Direction.up, Direction.down):
            return list(self.move_vertical(direction, apply))
        return list(self.move_horizontal(direction, apply))

    def resize(self, rows=None, cols=None):
        if rows:
            if rows < len(self):
                del self[rows:]
            elif rows > len(self):
                columns = cols or len(self[0])
                for _ in range(rows - len(self)):
                    self._grid.append([None for _ in range(columns)])

        if cols:
            for row in self:
                if cols < len(row):
                    del row[cols:]
                elif cols > len(row):
                    row.extend([None for _ in range(cols - len(row))])
