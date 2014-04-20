import os
import json
from itertools import product

xdg_data_home = (os.environ.get('XDG_DATA_HOME') or
                 os.path.join(os.path.expanduser('~'), '.local', 'share'))
macht_data_dir = os.path.join(xdg_data_home, 'macht')


def grid_to_dict(grid):
    tiles = []
    tile_base = 0
    for row_idx, col_idx in product(range(len(grid)), range(len(grid[0]))):
        if grid[row_idx][col_idx]:
            tile = grid[row_idx][col_idx]
            tile_base = tile.base
            tiles.append({'row': row_idx, 'column': col_idx,
                          'exponent': tile.exponent})
    return {'rows': len(grid), 'cols': len(grid[0]), 'base': tile_base,
            'tiles': tiles}


def write_to_file(score, grids, filename=None):
    filename = filename or os.path.join(macht_data_dir, 'default_save.json')
    try:
        os.makedirs(os.path.dirname(filename))
    except getattr(__builtins__, 'FileExistsError', OSError) as err:
        if err.errno != 17:  # py2: OSerror but not file exists
            raise

    contents = {'score': score,
                'grids': [grid_to_dict(grid) for grid in grids]}

    with open(filename, 'w') as save_file:
        json.dump(contents, save_file, indent=2)


def load_from_file(filename=None):
    filename = filename or os.path.join(macht_data_dir, 'default_save.json')

    try:
        with open(filename) as save_file:
            return json.load(save_file)
    except getattr(__builtins__, 'FileNotFoundError', IOError) as err:
        if err.errno != 2:  # py2: IOerror but not file not found
            raise
        return {}
