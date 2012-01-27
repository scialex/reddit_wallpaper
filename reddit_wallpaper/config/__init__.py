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
This module is responsible for parsing the input from the cli and from any config
files.
"""

from argparse import Namespace
from copy import deepcopy
from collections import namedtuple
from os.path import realpath, expandvars, expanduser
from .cli import parse_cmd_line
from ..platforms import DEFAULT_SAVE_LOCATION
from ..loggers import quiet, debug, normal

DEFAULT_LOG_LEVEL = 'debug'#change later

_DEFAULT_PICTURE_TYPES = ('png', 'jpg', 'jpeg', 
                          'gif', 'svg', 'bmp')

_LOGGERS = {'quiet'  : quiet,
            'debug'  : debug,
            'normal' : normal}

_DEFAULT_NSPACE = Namespace(overwrite  = False, # do not overwrite files
                            num_tries  = None,  # try all submissions the request gives you
                            save_file  = DEFAULT_SAVE_LOCATION,
                            endings    = _DEFAULT_PICTURE_TYPES,
                            subreddit  = ['wallpaper', 'wallpapers'],
                            sort_type  = '',
                            allow_nsfw = False,
                            min = [None, None],
                            max = [None, None],
                            logger = DEFAULT_LOG_LEVEL,
                            respect_flickr_nodownload = True,
                            messages = [])

configuration = namedtuple("configuration",
                           ["overwrite",
                            "num_tries",
                            "save_file",
                            "picture_endings",
                            "subreddit",
                            "allow_nsfw",
                            "size_limit",
                            "respect_flickr_nodownload",
                            "logger"])

size_limit = namedtuple("size_limit",
                        ["min_x", "min_y",
                         "max_x", "max_y"])
def get_config():
    """
    gets the configuration that this program is running with using the command line
    argument and (eventually) the config files.
    """
    return _convert_to_configuration(parse_cmd_line(deepcopy(_DEFAULT_NSPACE)))

def _convert_to_configuration(nspace):
    """
    This function should only be called from within this module.
    This function takes in a nspace (which must have all the required fields) and converts it into a
    configuration object. It will also print out any messages that have been queued up, using the specified
    logger. These messages will usually be warnings about unknown options or other such stuff.
    """
    conf = configuration(overwrite = nspace.overwrite,
                         num_tries = nspace.num_tries,
                         save_file = realpath(expandvars(expanduser(nspace.save_file))),
                         picture_endings = nspace.endings,
                         subreddit = '+'.join(nspace.subreddit) + '/' + nspace.sort_type,
                         allow_nsfw = nspace.allow_nsfw,
                         size_limit = None if [None, None] == nspace.min == nspace.max else size_limit(*(nspace.min + nspace.max)),
                         respect_flickr_nodownload = nspace.respect_flickr_nodownload,
                         logger = _LOGGERS[nspace.logger])
    if hasattr(nspace, 'messages'):
        for msg in nspace.messages:
            conf.logger(*msg)
    return conf
