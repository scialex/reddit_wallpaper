#!/usr/bin/python

import json, gconf, syslog, os
from syslog import LOG_DEBUG as DEBUG, LOG_INFO as INFO, LOG_WARNING as WARNING, LOG_ERR as ERROR
from collections import namedtuple
from urllib2 import urlopen, HTTPError

#temporary
logit = syslog.syslog

configuration = namedtuple("configuration",
                           ["overwrite",
                            "num_tries",
                            "save_location",
                            #"gconf_key",#this should be same everywhere
                            "picture_endings",
                            "subreddit"])



#THE DEFAULT CONFIGURATION SETTINGS
OVERWRITE = False
SYSLOG_IDENT = 'wallpaper_rotater-dev'#name in the log
#the min log_level. should put to LOG_WARNING after done testing
SYSLOG_LOGMASK = syslog.LOG_UPTO(DEBUG)
NUMBER_TRIES = 3 #how many subbmission will it look at?
SAVE_LOCATION = os.path.join(os.path.expanduser('~'), '.background_getter')
GCONF_KEY = '/desktop/gnome/background/picture_filename'#key to write new wallpaper to
PICTURE_ENDINGS=['png','jpg','jpeg','gif']#picture endings
JSON_PAGE_FORMAT = 'http://www.reddit.com/r/{0}.json'#where the list of possible wallpapers is
IMGUR_JSON_FORMAT = "http://api.imgur.com/2/image/{0}.json"
SUBREDDIT = "wallpaper+wallpapers"

class Failed(Exception):
    pass
class Unsuccessful(Exception):
    pass

def start_update(conf):
    json_data = json.loads(urlopen(JSON_PAGE_FORMAT.format(conf.subreddit)).read())["data"]["children"]
    imageURL, post_id = get_image_data(conf, json_data)
    logit(INFO, "Postid for the image is {0}".format(post_id))
    save_name = os.path.join(conf.save_location,
                             #the name will be <id>.<file_type>
                             "".join((post_id,'.', imageURL.split('.')[-1])))
    write_file(conf, imageURL, save_name)
    set_as_background(conf, save_name)
    return

def write_file(conf, url, save_name):
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

def get_image_data(conf, data):
    for child in data[0:conf.num_tries]:

        if child["data"]["thumbnail"] == "nsfw":
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
            url = data["image"]['links']["original"]
            logit(INFO, 'found {0}, link was not direct'.format(url))
            return url, child['data']['id']
    logit(syslog.LOG_WARNING, "none of the possibilities could be used")
    raise Failed("could not get a suitable url")

def set_as_background(conf, file_location):
   # assert type(file_location) is type("a string")
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
    conf = configuration(overwrite = OVERWRITE,
                         num_tries = NUMBER_TRIES,
                         save_location = SAVE_LOCATION,
                         picture_endings = PICTURE_ENDINGS,
                         subreddit = SUBREDDIT)
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

