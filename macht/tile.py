class Tile(object):
    _base = 0
    _exponent = 1

    def __init__(self, base=2, exponent=1):
        self.base = base
        self.exponent = exponent

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, value):
        self._base = value
        self.value = self._base ** self.exponent

    @property
    def exponent(self):
        return self._exponent

    @exponent.setter
    def exponent(self, value):
        self._exponent = value
        self.value = self.base ** self._exponent

    def __eq__(self, other):
        return (isinstance(other, Tile) and self.base == other.base and
                self.exponent == other.exponent)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, Tile):
            raise NotImplementedError

        return self.value < other.value

    def __repr__(self):
        return "Tile(base={}, exponent={})".format(self.base, self.exponent)
