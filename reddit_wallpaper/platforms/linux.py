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

import gconf
from .. import _exceptions
from ..loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY

_GCONF_KEY = '/desktop/gnome/background/picture_filename'#key to write new wallpaper to
DEFAULT_SAVE_LOCATION = '~/.background_getter/@'

def set_as_background(conf, file_location):
    """Sets the background path to the given path"""
    client = gconf.client_get_default()
    worked = client.set_string(_GCONF_KEY, file_location)
    client.suggest_sync()
    if worked:
        conf.logger(DEBUG, 'changed the background succsessfully')
    else:
        conf.logger(ERROR, 'was unable to change the background, gconf client reported failure of key setting.')
        raise _exceptions.Failed("could not set gconf key")
    return

__all__ = ['DEFAULT_SAVE_LOCATION', 'set_as_background']
