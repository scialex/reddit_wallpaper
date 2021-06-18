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
# from os.path import dirname, join
# from ctypes import windll
# from PIL import Image
import subprocess
from .. import _exceptions
from ..loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY

DEFAULT_SAVE_LOCATION = '~/_background_getter/@'
POWERSHELL_COMMAND="set-wallpaper"

def set_as_background(conf, file_location):
    """
    
    """
    subprocess.run(['powershell', '-Command', '{} {}'.format(POWERSHELL_COMMAND, file_location)])
    # bmp_file_name = join(dirname(file_location), current_wallpaper.bmp)
    # fle = open(file_location, 'rb')
    # img = Image.open(fle)
    # outfile = open(bmp_file_name, 'w')
    # img.save(outfile, 'BMP')
    # outfile.close()
    # outfile.flush()
    # os.fsync(outfile.fileno())
    # result = windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, bmp_file_name, SPIF_SENDWININICHANGE | SPIF_UPDATEINIFILE)
    # if not result: # == 1
    #     conf.logger(ERROR, "was unable to set the registry key to change the wallpaper")
    #     raise _exceptions.Failed('was unable to set the registry key needed to change the wallpaper')
    # else:
    #     conf.logger(INFO, "changed the wallpaper successfully")
    # return 
        
__all__ = ['DEFAULT_SAVE_LOCATION', 'set_as_background']
