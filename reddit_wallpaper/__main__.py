#!/usr/bin/python

from reddit_wallpaper import _exceptions
from reddit_wallpaper.background_getter import start_update
from reddit_wallpaper.config import get_config
from reddit_wallpaper.loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY
from urllib2 import HTTPError

def main():
    conf = get_config()
    conf.logger(INFO, 'Starting change of wallpaper')
    try:
        start_update(conf)
    except _exceptions.Failed as f:
        conf.logger(WARNING,
                    'Failed to update wallpaper, reason was {0}'.format(f.args[0]))
    except _exceptions.Unsuccessful as u:
        conf.logger(INFO, "Did not change wallpaper")
    except HTTPError as h:
        conf.logger(ERROR,
                    "An HTTPError was thrown, reason given was {0}".format(str(h)))
    except Exception as e:
        conf.logger(ERROR,
                    'an uncaught exception was thrown, reason given was {0}, type was given as {1}, args were {2}'.format(e.args[0], type(e), e.args))
    else:
        conf.logger(INFO, 'all done changing wallpaper')
main()
