#!/usr/bin/python

import json, gconf, syslog, os
from syslog import LOG_DEBUG as DEBUG, LOG_INFO as INFO, LOG_WARNING as WARNING
from urllib2 import urlopen



SYSLOG_IDENT = 'wallpaper-rotater'#name in the log
#the min log-level. should put to LOG_WARNING after done testing
SYSLOG_LOGMASK = syslog.LOG_UPTO(syslog.LOG_WARNING)
NUMBER_TRIES = 3 #how many subbmission will it look at?
SAVE_LOCATION = os.path.join(os.path.expanduser('~'), '.background_getter')
GCONF_KEY = '/desktop/gnome/background/picture_filename'#key to write new wallpaper to
PICTURE_ENDINGS=['png','jpg','jpeg','gif']#picture endings
JSON_PAGE = 'http://www.reddit.com/r/wallpaper+wallpapers.json'#where the list of possible wallpapers is
IMGUR_JSON_FORMAT = "http://api.imgur.com/2/image/{0}.json"

class Failed(Exception):
    pass

def main():
    json_data = json.loads(urlopen(JSON_PAGE).read())["data"]["children"]
    imageURL, post_id = get_image_data(json_data)
    save_name = os.path.join(SAVE_LOCATION,
                             #the name will be <id>.<file-type>
                             "".join((post_id,'.',imageURL.split('.')[-1])))
    if not os.access(save_name, os.F_OK):
        syslog.syslog(INFO, "saving to {0}".format(save_name))
        with open(save_name, 'wb') as f:
            f.write(urlopen(imageURL).read())
            f.flush()
            os.fsync(f.fileno())
    #else:
    #    return
    set_as_background(save_name)
    return
    
def get_image_data(data):
    for child in data[0:NUMBER_TRIES]:
        if child["data"]["thumbnail"] == "nsfw":
            continue
        if child["data"]["domain"] == "i.imgur.com":
            url = child["data"]["url"]
            syslog.syslog(INFO, 'found {0}, link was direct to i.imgur.com'.format(url))
            return url, child['data']['id']
        elif child['data']['url'].split('.')[-1] in PICTURE_ENDINGS:
            url = child['data']['url']
            syslog.syslog(INFO, 'found {0}, link was direct to a non-imgur site'.format(url))
            return url, child['data']['id']
        elif child["data"]["domain"] == "imgur.com":
            name = child["data"]["url"].split('/')[-1]
            data = json.loads(urlopen(IMGUR_JSON_FORMAT.format(name)).read())
            url = data["image"]['links']["original"]
            syslog.syslog(INFO, 'found {0}, link was not direct'.format(url))
            return url, child['data']['id']
    syslog.syslog(syslog.LOG_WARNING, "none of the possibilities could be used")
    raise Failed("could not get url")

def set_as_background(file_location):
   # assert type(file_location) is type("a string")
    client = gconf.client_get_default()
    worked = client.set_string(GCONF_KEY,file_location)
    client.suggest_sync()
    if worked:
        syslog.syslog(DEBUG, 'changed the background succsessfully')
    else:
        syslog.syslog(syslog.LOG_ERR, 'was unable to change the background')
        raise Failed("could not set gconf key")
    return
    
if __name__ == '__main__':
    syslog.openlog(SYSLOG_IDENT)
    syslog.setlogmask(SYSLOG_LOGMASK)
    syslog.syslog(INFO, 'Starting change of wallpaper')
    try:
        main()
    except Failed as f:
        syslog.syslog(WARNING,
                      'Failed to update wallpaper, reason was {0}'.format(f.args[0]))
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR,
                      'an uncaught exception was thrown, reason given was {0}'.format(e.args[0]))
    syslog.syslog(INFO, 'all done changing wallpaper')
    syslog.closelog()
