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

import gconf
import imagefacts
import json
import os
from urllib2 import urlopen, HTTPError
from config import *
from loggers import *

#THE DEFAULT CONFIGURATION SETTINGS
default_conf = configuration(overwrite = False,
                             num_tries = None,
                             save_location = os.path.join(os.path.expanduser('~'),
                                                          '.background_getter'),
                             save_file = '@',
			     picture_endings = ['png', 'jpg', 'jpeg', 'gif'],
                             subreddit  = 'wallpaper+wallpapers',
			     allow_nsfw = False,
			     size_limit = None,
			     logger = debug)#size_limit(0,0,1660,1000))

GCONF_KEY = '/desktop/gnome/background/picture_filename'#key to write new wallpaper to
JSON_PAGE_FORMAT = 'http://www.reddit.com/r/{0}.json'#where the list of possible wallpapers is
IMGUR_JSON_FORMAT = "http://api.imgur.com/2/image/{0}.json"#imgur api page
FLICKR_JSON_FORMAT = 'http://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=eaf4581fb8d0655b0a314d13ab54ef46&photo_id={0}&format=json&nojsoncallback=1'

class Failed(Exception):
    """
    This is used when there is a failure and it was not compleatly
    unexpected but was totally fatal (i.e. no internet)
    """
    pass

class Unsuccessful(Exception):
    """
    This is used when there is a failure but it is not fatal
    """
    pass


def start_update(conf):
    """Updates the background image using the configuration stored in conf"""
    json_data = json.loads(urlopen(
                   JSON_PAGE_FORMAT.format(conf.subreddit)).read())["data"]["children"]
    conf.logger(DEBUG,
                "retrieved json page from reddit successfully")
    imageURL, post_id = select_image(conf, json_data)
    conf.logger(INFO, "Postid for the image is {0}".format(post_id))
    save_name = os.path.join(conf.save_location,
                             #the name will be <id>.<file_type>
                             ".".join((conf.save_file.replace('@', post_id),
			               imageURL.split('.')[-1])))
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
            raise Failed("Unwritable save location")

        conf.logger(INFO, "saving to {0}".format(save_name))
        with open(save_name, 'wb') as f:
            f.write(urlopen(url).read())
            f.flush()
            os.fsync(f.fileno())
    else:
        conf.logger(WARNING, "there is already a file at {0}".format(save_name))
    return

def check_size(conf, img_size):
    """
    this takes in the configuration object and a 2-tuple containing the x and 
    y sizes of the image. it returns true if the size is permitted by the 
    configuration given
    """
    if img_size is None:
	return True # we were not able to determine the size of the image
    size_limit = conf.size_limit
    x = img_size[0]
    y = img_size[1] 
    return size_limit is None or ((size_limit.min_x is None or x >= size_limit.min_x) and
				  (size_limit.max_x is None or x <= size_limit.max_x) and
				  (size_limit.min_y is None or y >= size_limit.min_y) and
				  (size_limit.max_y is None or y <= size_limit.max_y))

def select_image(conf, data):
    """
    Selects a background image from the data conforming to the configuration
    and returns its url as well as its reddit post-id number
    """
    for child in data[0:conf.num_tries]:
        url = child["data"]["url"]
        if conf.allow_nsfw == False and child["data"]["thumbnail"] == "nsfw":
	    conf.logger(INFO, "the image at {0} was marked NSFW, skiping".format(url))
            continue

        elif child["data"]["domain"] == "i.imgur.com":
	    try:
		data = json.loads(urlopen(IMGUR_JSON_FORMAT.format(url.split('/')[-1][:5])).read())
		conf.logger(DEBUG,
		            "was able to retrieve the image metadata from imgur for image {0}".format(url))
	    except HTTPError:
		continue
	    if not check_size(conf,
			      (data["image"]["image"]["width"],
			       data["image"]["image"]["height"])):
		conf.logger(DEBUG,
		            "the image at {0} was not the right size".format(url))
		continue
            conf.logger(INFO, 'found {0}, link was direct to i.imgur.com'.format(url))
            return url, child['data']['id']
	
	elif child["data"]["domain"] == 'flickr.com':
	    try:
		#the url splits into ['http:','','www.flickr,com','photos','username','photoid',etc]
		#                       0      1           2          3       4          *5*    etc
		photo_id = url.split('/')[5]
		conf.logger(DEBUG, 'flickr link found. url is {0}, photo_id determined to be {1}'.format(url, photo_id))
		data = json.loads(urlopen(FLICKR_JSON_FORMAT.format(photo_id)).read())
	        if data['stat'] != 'ok':
		    conf.logger(WARNING, "got a failure response from the flickr api. status was given as {0}. message was given as {1}. skipping this link".format(data['stat'], data['message']))
		    continue
	        return choose_flickr_size(conf, data), child['data']['id']
	    except HTTPError as h:
		conf.logger(WARNING, "an HTTPError was caught, reason given was {0}. skipping this link".format(str(h)))
		continue
	    except Unsuccessful:
		conf.logger(DEBUG, "flickr did not have any link that was the right size")
		continue
        elif child['data']['url'].split('.')[-1] in conf.picture_endings:
	    try:
		if conf.size_limit is not None:
		    size = imagefacts.facts(url)[1:]
		else:
		    size = None 
	    except Exception as e:
		conf.logger(WARNING,
		            "something happened while trying to retrieve the image at {0} in order to determine its size. type of exception was {1} and reason given was {2}".format(url, type(e), e.args))
		continue	
	    if not check_size(conf, size):
		conf.logger(DEBUG,
		            "the image at {0} was not the right size".format(url))
		continue
            conf.logger(INFO, 'found {0}, link was direct to a non_imgur site'.format(url))
            return url, child['data']['id']

        elif child["data"]["domain"] == "imgur.com":
            name = child["data"]["url"].split('/')[-1]
            try:
                data = json.loads(urlopen(IMGUR_JSON_FORMAT.format(name)).read())
            except HTTPError:
		conf.logger(WARNING,
		            "was unable to use the imgur api to determine the size of the image at {0}, skiping".format(url))
                continue
	    #check if the size is right
            if not check_size(conf, (data["image"]["image"]["width"],
			             data["image"]["image"]["height"])):
		continue
		
	    url = data["image"]["links"]["original"]
            conf.logger(INFO, 'found {0}, link was not direct'.format(url))
            return url, child['data']['id']
    conf.logger(WARNING, "none of the possibilities could be used")
    raise Failed("could not get a suitable url")

def choose_flickr_size(conf, data):
    best = None
    best_size = (0,0)
    for pic in data['sizes']['size']:
	pic['width'] = int(pic['width'])
	pic['height'] = int(pic['height'])
	if (check_size(conf, (pic['width'], pic['height'])) and
	    pic['width']  >= best_size[0] and
	    pic['height'] >= best_size[1]):
	    best_size = (pic['width'], pic['height'])
	    best = pic
    if best is None:
	raise Unsuccessful()
    else:
	conf.logger(DEBUG, 'chose size to be one labled {0}'.format(best['label']))
	return best['source'].replace('\\','')

def set_as_background(conf, file_location):
    """Sets the background path to the given path"""
    client = gconf.client_get_default()
    worked = client.set_string(GCONF_KEY,file_location)
    client.suggest_sync()
    if worked:
        conf.logger(DEBUG, 'changed the background succsessfully')
    else:
        conf.logger(ERROR, 'was unable to change the background')
        raise Failed("could not set gconf key")
    return

def main():
    #print repr(parse_cmd_line())
    conf = get_config()#default_conf
    #syslog.openlog(SYSLOG_IDENT)
    #syslog.setlogmask(SYSLOG_LOGMASK)
    conf.logger(INFO, 'Starting change of wallpaper')
    try:
        start_update(conf)
    except Failed as f:
        conf.logger(WARNING,
                    'Failed to update wallpaper, reason was {0}'.format(f.args[0]))
    except Unsuccessful as u:
        conf.logger(INFO, "Did not change wallpaper")
    except HTTPError as h:
        conf.logger(ERROR, 
                    "An HTTPError was thrown, reason given was {0}".format(str(h)))
    except Exception as e:
        conf.logger(ERROR,
                    'an uncaught exception was thrown, reason given was {0}, type was given as {1}, args were {2}'.format(e.args[0], type(e), e.args))
    else:
        conf.logger(INFO, 'all done changing wallpaper')

if __name__ == '__main__':
    main()
