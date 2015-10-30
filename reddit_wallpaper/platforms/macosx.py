# Copyright 2015, Alex Light.
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


from .. import _exceptions
from ..loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY
import subprocess

DEFAULT_SAVE_LOCATION = '~/.background_getter/@'

def _log_succsess(conf, mod = None):
    msg = 'changed the background{0} succsessfully'
    if mod is not None:
        msg = msg.format(" ".join((" in",str(mod))))
    else:
        msg = msg.format("")
    conf.logger(DEBUG, msg)

def _log_failed(conf):
    msg = 'was unable to change the background'
    conf.logger(ERROR, msg)

SET_AS_BACKGROUND_SCRIPT = """
/usr/bin/osascript <<END
tell application "Finder"
    set desktop picture to POSIX file {0}
end tell
END
"""
def set_as_background(conf, file_location):
    try:
        subprocess.check_call(SET_AS_BACKGROUND_SCRIPT.format(file_location), shell=True)
        _log_succsess(conf)
    except e:
        _log_failed(conf)
        raise
    return

__all__ = ['DEFAULT_SAVE_LOCATION', 'set_as_background']
