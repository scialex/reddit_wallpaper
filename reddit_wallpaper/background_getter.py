#!/usr/bin/python
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
#DONE add size min and max arguments
#DONE redo get image data so above will work.
#DONE make it work with command line argumentsa
#TODO make it work with more photo sites
#TODO refactor out code for handling different websites
#TODO make it work with a real config file
#TODO add a copyright notice to it GPL3+ maybe...
#TODO make better logging functionality, still with syslog just maybe also be able to tee it to stdout? IDK?
#TODO factor out all site/OS specific stuff to other files. (i.e. gconf)
#TODO make it work on windows and OSX
#TODO give it a TK gui
#TODO integrate it with pycrontab and windows scheduler so can have scheduled things
#TODO package it
#TODO profit

"""
This module facilitates the actual calling of all the others,
it is the glue that holds everything together
"""

if __name__ == "__main__" and __package__ is None:
    __package__ = "reddit_wallpaper.background_getter"
import gconf
import imagefacts
import json
import os
from . import _exceptions
from urllib2 import urlopen, HTTPError
from .loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY
from .websites import select_image
from .websites.handlers import default_handlers

GCONF_KEY = '/desktop/gnome/background/picture_filename'#key to write new wallpaper to
JSON_PAGE_FORMAT = 'http://www.reddit.com/r/{0}.json'#{0} is the subreddits name. This is where the list of possible wallpapers is

def start_update(conf, handlers = default_handlers):
    """Updates the background image using the configuration stored in conf"""
    json_data = json.loads(urlopen(
                   JSON_PAGE_FORMAT.format(conf.subreddit)).read())["data"]["children"]
    conf.logger(DEBUG,
                "retrieved json page from reddit successfully")
    imageURL, post_id = select_image(conf, json_data, handlers)
    conf.logger(INFO, "Postid for the image is {0}".format(post_id))
    save_name = '.'.join((conf.save_file.replace('@', post_id),# <- the filename
                          imageURL.split('.')[-1])) # <- the filetype
    write_file(conf, imageURL, save_name)
    set_as_background(conf, save_name)
    return

def write_file(conf, url, save_name):
    """
    Takes in a configuration object, the url string and a file name
    It will attempt to download the file at the url and will save it
    to the given location, if there is already a file at save_name it
    will niether download nor save the file.
    """
    if conf.overwrite or not os.access(save_name, os.F_OK):
        if not os.access(os.path.dirname(save_name), os.W_OK):
            conf.logger(ERROR, "The location {0} is not writable by this process".format(save_name))
            raise _exceptions.Failed("Unwritable save location")

        conf.logger(INFO, "saving to {0}".format(save_name))
        with open(save_name, 'wb') as f:
            f.write(urlopen(url).read())
            f.flush()
            os.fsync(f.fileno())
    else:
        conf.logger(WARNING, "there is already a file at {0}".format(save_name))
    return

def set_as_background(conf, file_location):
    """Sets the background path to the given path"""
    client = gconf.client_get_default()
    worked = client.set_string(GCONF_KEY,file_location)
    client.suggest_sync()
    if worked:
        conf.logger(DEBUG, 'changed the background succsessfully')
    else:
        conf.logger(ERROR, 'was unable to change the background')
        raise _exceptions.Failed("could not set gconf key")
    return
