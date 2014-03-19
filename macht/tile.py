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
        return isinstance(other, Tile) and self.value == other.value

    def __repr__(self):
        return "Tile({}, {})".format(self.base, self.exponent)
