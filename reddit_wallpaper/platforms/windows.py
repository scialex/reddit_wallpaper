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
import os
from os.path import dirname, join
from ctypes import windll
from PIL import Image
from .. import _exceptions
from ..loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 1
SPIF_SENDWININICHANGE = 2

def set_as_background(conf, file_location):
    """
    Sets the background path to the given path. It does this by making a copy as a bitmap and 
    setting the wallpaper to that. The bitmap is always stored at the file's location and named
    current_wallpaper.bmp
    """
    bmp_file_name = join(dirname(file_location), current_wallpaper.bmp)
    with fle as open(file_location, 'rb'):
        img = Image.open(fle)
        outfile = open(bmp_file_name, 'w')
        img.save(outfile, 'BMP')
        outfile.close()
        outfile.flush()
        os.fsync(f.fileno())
    result = windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, bmp_file_name, SPIF_SENDWININICHANGE | SPIF_UPDATEINIFILE)
    if not result: # == 1
        conf.logger(ERROR, "was unable to set the registry key to change the wallpaper")
        raise _exceptions.Failed('was unable to set the registry key needed to change the wallpaper')
    else:
        conf.logger(INFO, "changed the wallpaper successfully")
    return 
        
