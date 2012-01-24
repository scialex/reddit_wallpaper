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

import sys

set_as_background = lambda a, b: None

if sys.platform.startswith('linux'):
    from .linux import set_as_background as sab
    set_as_background = sab
elif sys.platform.startswith('win32'):
    from .windows import set_as_background as sab
    set_as_background = sab
elif sys.platform.startswith('darwin'):
    from .macosx import set_as_background as sab
    set_as_background = sab

__all__ = [set_as_background]
