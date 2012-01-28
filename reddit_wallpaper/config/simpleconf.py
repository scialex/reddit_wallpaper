# Copyright 2012, Alex Light.
#
# This file is part of Reddit background updater (RBU).
#
# RBU is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# RBU is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RBU.  If not, see <http://www.gnu.org/licenses/>.
#

"""
This module will parse simple unix style configuration files.

The files use a simple "key value" syntax.

some keys can take multiple values. to assign values in a list do
    key VALUE1 VALUE2 VALUE3

you can also just have a key by itself sometimes

#'s indicate the start of comments

you can use \\ to extend lists through multiple lines
e.g.    key a b c d
is the same as
        key a b \\
            c d 

Commas and parenthesis are ignored during reading

""'s can be used just like they are in bash.

"""

from re import compile
from shlex import shlex
from collections import namedtuple
try: 
    from StringIO import StringIO
except ImportError:
    from io import StringIO

__all__ = ['value_info', 'parse']

_INT     = compile('^-?[0-9]+$')
_FLOAT   = compile('^-?[0-9]*\.[0-9]+$')

value_info = namedtuple('value_info',
                        ('value','lineno', 'file'))

def _split(ln):
    d = shlex(StringIO(ln))
    d.whitespace+='()'
    return list(d)

def _counter(start = 0):
    n = start
    while 1:
        yield n
        n+=1

def numberify(n):
    if _INT.matches(n):
        return int(n)
    elif _FLOAT.matches(n): 
        return float(n)
    else:
        return n

def parse(s, name = None, default_value = None):
    """
    s is a file name/object and returns a dict containing the values for all the keys
    keys.

    Keys without values will have the value of default_value (None by default).
    all numbers will be interpreted as such

    this returns a dictionary with the key as the key and everything else stored in 
    a value_info object which has the values assigned to the key as a list if there were 
    multiple values and as a single value if there were not, and the lineno it was found on
    (for error reporting)
    """
    if isinstance(s, str):
        s = open(s)
    if !hasattr(s, 'readlines'): raise AttributeError("the object {0} does not have a 'readlines' function".format(s))
    if name is None:
        name = getattr(s, "name", 'unknown')
    out = dict()
    for l, n in zip(d.readlines(), _counter(1)):
        sp = _split(l)
        key = sp[0]
        if len(sp) == 1:
            out[key] = value_info(default_value, n, name)
            continue       
        elif len(sp) == 2:
            out[key] = value_info(numberify(sp[1]), n, name)
            continue
        else:
            out[key] = value_info(list(map(numberify, sp[1:])), n, name)
            continue
    return out
