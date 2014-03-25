import pytest
from macht import tile


def test_properties():
    t = tile.Tile(base=2, exponent=1)
    assert t.base == 2 and t.exponent == 1
    assert t.value == 2 ** 1

    t = tile.Tile(3, 2)
    assert t.base == 3 and t.exponent == 2
    assert t.value == 3 ** 2

    t.base = 5
    assert t.base == 5
    t.exponent = 3
    assert t.exponent == 3

    assert t.value == 5 ** 3


def test_cmp():
    t = tile.Tile()
    t.base, t.exponent = 3, 3
    assert t == tile.Tile(3, 3)
    assert t != tile.Tile(2, 1)
    assert t != 3 ** 3  # a tile is not just it's value

    t = tile.Tile(2, 4)
    assert t != tile.Tile(4, 2)
    assert t < tile.Tile(2, 5) and t > tile.Tile(2, 3)
    assert t < tile.Tile(3, 3) and t > tile.Tile(3, 2)

    assert tile.Tile(2, 1) == tile.Tile(2, 1)
    assert not tile.Tile(2, 1) != tile.Tile(2, 1)

    with pytest.raises(NotImplementedError):
        t < 2 ** 5


def test_repr():
    from macht.tile import Tile

    assert repr(tile.Tile()) == 'Tile(base=2, exponent=1)'
    eval(repr(tile.Tile()))
