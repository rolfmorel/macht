from collections import namedtuple

components = 'major, minor, micro, releaselevel, serial'
values = (0, 1, 0, 'final', 0)
__version_info__ = namedtuple('__version_info__', components)(*values)
__version__ = (str(__version_info__.major) + '.' +
               str(__version_info__.minor))
del components, values
