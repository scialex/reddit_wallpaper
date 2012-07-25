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
__author__ = "Alexander Light"

#from reddit_wallpaper import _exceptions
#from reddit_wallpaper.background_getter import start_update
#from reddit_wallpaper.config import get_config
#from reddit_wallpaper.loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY
try:
    from urllib2 import build_opener, install_opener, HTTPError
except ImportError:
    from urllib.request import build_opener, install_opener
    from urllib.error import HTTPError
from . import _exceptions
from .background_getter import start_update
from .config import get_config
from .loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY

def main():
    conf = get_config()
    conf.logger(INFO, 'Starting change of wallpaper')
    try:
        opener = build_opener()
        opener.addheaders = [('User-agent','reddit-wallpaper-program')]
        install_opener(opener)
        start_update(conf)
    except _exceptions.Failed as f:
        conf.logger(WARNING,
                    'Failed to update wallpaper, reason was {0}'.format(f.args[0]))
    except _exceptions.Unsuccessful as u:
        conf.logger(INFO, "Did not change wallpaper")
    except HTTPError as h:
        conf.logger(ERROR,
                    "An HTTPError was thrown, reason given was {0}".format(str(h)))
#    except Exception as e:
#        conf.logger(ERROR,
#                    'an uncaught exception was thrown, reason given was {0}, type was given as {1}, args were {2}'.format(e.args[0], type(e), e.args))
#    else:
#        conf.logger(INFO, 'all done changing wallpaper')
#
