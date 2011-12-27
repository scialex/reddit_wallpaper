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
#TODO add size min and max arguments
#TODO redo get image data so above will work.
#TODO make it work with command line arguments
#TODO make it work with a real config file
#TODO add a copyright notice to it GPL3+ maybe...
#TODO make better logging functionality, still with syslog just maybe also be able to tee it to stdout? IDK?
#TODO factor out all site/OS specific stuff to other files. (i.e. gconf)
#TODO make it work on windows and OSX
#TODO give it a TK gui
#TODO integrate it with pycrontab and windows scheduler so can have scheduled things
#TODO package it
#TODO profit

import json
import gconf
import syslog
import  os
from syslog import LOG_DEBUG as DEBUG, LOG_INFO as INFO, LOG_WARNING as WARNING, LOG_ERR as ERROR
from collections import namedtuple
from urllib2 import urlopen, HTTPError

#temporary will change to better logging system.
logit = syslog.syslog

configuration = namedtuple("configuration",
                           ["overwrite",
                            "num_tries",
                            "save_location",
                            "picture_endings",
                            "subreddit",
                            "allow_nsfw",
			    "size_limit"])

#THE DEFAULT CONFIGURATION SETTINGS
default_conf = configuration(overwrite = False,
                             num_tries = None,
                             save_location = os.path.join(os.path.expanduser('~'),
                                                          '.background_getter'),
                             picture_endings = ['png', 'jpg', 'jpeg', 'gif'],
                             subreddit  = 'wallpaper+wallpapers',
			     allow_nsfw = False,
			     size_limit = None)
SYSLOG_IDENT = 'wallpaper_rotater-dev'#name in the log
#the min log_level. should put to LOG_WARNING after done testing
SYSLOG_LOGMASK = syslog.LOG_UPTO(DEBUG)
GCONF_KEY = '/desktop/gnome/background/picture_filename'#key to write new wallpaper to
JSON_PAGE_FORMAT = 'http://www.reddit.com/r/{0}.json'#where the list of possible wallpapers is
IMGUR_JSON_FORMAT = "http://api.imgur.com/2/image/{0}.json"#imgur api page

class Failed(Exception):
    pass
class Unsuccessful(Exception):
    pass

size_limit = namedtuple("size_limit",
			["min_x","min_y",
			 "max_x","max_y"])

def start_update(conf):
    """Updates the background image using the configuration stored in conf"""
    json_data = json.loads(urlopen(JSON_PAGE_FORMAT.format(conf.subreddit)).read())["data"]["children"]
    imageURL, post_id = select_image(conf, json_data)
    logit(INFO, "Postid for the image is {0}".format(post_id))
    save_name = os.path.join(conf.save_location,
                             #the name will be <id>.<file_type>
                             ".".join((post_id, imageURL.split('.')[-1])))
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
            logit(ERROR, "The location {0} is not writable by this process".format(save_name))
            raise Failed("Unwritable save location")

        logit(INFO, "saving to {0}".format(save_name))
        with open(save_name, 'wb') as f:
            f.write(urlopen(url).read())
            f.flush()
            os.fsync(f.fileno())
    else:
        logit(WARNING, "there is already a file at {0}".format(save_name))
    return

def check_size(conf, img_size):
    """
    this takes in the configuration object and a 2-tuple containing the x and 
    y sizes of the image. it returns true if the size is permitted by the 
    configuration given
    """
    size_limit = conf.size_limit
    x = img_size[0]
    y = img_size[1] 
    return size_limit is None or (x >= size_limit.min_x and
				  x <= size_limit.max_x and
				  y >= size_limit.min_y and
				  y <= size_limit.max_y)


def select_image(conf, data):
    """
    Selects a background image from the data conforming to the configuration
    and returns its url as well as its reddit post-id number
    """
    for child in data[0:conf.num_tries]:
        if conf.allow_nsfw == False and child["data"]["thumbnail"] == "nsfw":
            continue

        elif child["data"]["domain"] == "i.imgur.com":
            url = child["data"]["url"]
            logit(INFO, 'found {0}, link was direct to i.imgur.com'.format(url))
            return url, child['data']['id']

        elif child['data']['url'].split('.')[-1] in conf.picture_endings:
            url = child['data']['url']
            logit(INFO, 'found {0}, link was direct to a non_imgur site'.format(url))
            return url, child['data']['id']

        elif child["data"]["domain"] == "imgur.com":
            name = child["data"]["url"].split('/')[-1]
            try:
                data = json.loads(urlopen(IMGUR_JSON_FORMAT.format(name)).read())
            except HTTPError:
                continue
            url = data["image"]["links"]["original"]
            logit(INFO, 'found {0}, link was not direct'.format(url))
            return url, child['data']['id']
    logit(syslog.LOG_WARNING, "none of the possibilities could be used")
    raise Failed("could not get a suitable url")

def set_as_background(conf, file_location):
    """Sets the background path to the given path"""
    client = gconf.client_get_default()
    worked = client.set_string(GCONF_KEY,file_location)
    client.suggest_sync()
    if worked:
        logit(DEBUG, 'changed the background succsessfully')
    else:
        logit(ERROR, 'was unable to change the background')
        raise Failed("could not set gconf key")
    return

if __name__ == '__main__':
    conf = default_conf
    syslog.openlog(SYSLOG_IDENT)
    syslog.setlogmask(SYSLOG_LOGMASK)
    logit(INFO, 'Starting change of wallpaper')
    try:
        start_update(conf)
    except Failed as f:
        logit(WARNING,
              'Failed to update wallpaper, reason was {0}'.format(f.args[0]))
    except Unsuccessful as u:
        logit(INFO, "Did not change wallpaper")
    except HTTPError as h:
        logit(ERROR, 
              "An HTTPError was thrown, reason given was {0}".format(str(h)))
    except Exception as e:
        logit(ERROR,
              'an uncaught exception was thrown, reason given was {0}, type was given as {1}'.format(e.args[0], type(e)))
    else:
        logit(INFO, 'all done changing wallpaper')
    syslog.closelog()

