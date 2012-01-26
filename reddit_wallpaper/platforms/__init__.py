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
This module contains the code to set the wallpaper on different platforms
Only import this module it will load the appropriate submodule automatically
NB The calling of the provided set_as_background method may have side effects
"""

import sys
from .._exceptions import Failed

set_as_background = lambda a, b: None

if sys.platform.startswith('linux'):
    from .linux import * 
    __all__ = ['DEFAULT_SAVE_LOCATION', 'set_as_background']
elif sys.platform.startswith('win32'):
    from .windows import * 
    __all__ = ['DEFAULT_SAVE_LOCATION', 'set_as_background']
#elif sys.platform.startswith('darwin'):
#    from .macosx import set_as_background as sab
#    set_as_background = sab
else:
    raise Failed("There was no way to set the wallpaper for this platform")

