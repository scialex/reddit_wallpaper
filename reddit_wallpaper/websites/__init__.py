# Copyright 2012, Alex Light.
#
# This file is part of Reddit background updater (RBU).
#
#__package__ = 'reddit_wallpaper.websites'

from .handlers import default_handlers
from .._exceptions import *
try:
    from functools import cmp_to_key
except ImportError: # workaround for python2.6
    cmp_to_key = lambda a: a
    def sorted(a, key):
        return __builtins__.sorted(a, cmp=key) 

try:
    from itertools import ifilter as filter
except ImportError:
    pass
from ..loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY


def select_image(conf, data, handlers = default_handlers):
    """
    this function takes in the current configuration, the json data from reddit,
    and a list of handlers. each handler should have an added attribute 'acceptable'
    that is a function that takes in a reddit api organized reddit-post and returns
    true if through this data it will work. False if it will not. If it needs more
    info use the requires_runtime_checking decorator which will allow it to use all
    the information in the configuration object. you can also use the priority
    decorator to give each handler a decorator. Higher priorities go first. Also
    any function decorated with requires_runtime_authentication will be tried after
    all other handler's with the same priority. By default the priority is 100. all
    the default handlers have a priority of 100.
    """
    srt_handlers = sorted(handlers, key = cmp_to_key(_handler_cmp))
    for child in data[0:conf.num_tries]:
        conf.logger(INFO, "trying reddit post {0}, is a link to {1}.".format(child['data']['id'],
                                                                             child['data']['url']))
        if conf.allow_nsfw is False and child["data"]["over_18"] is True:
            conf.logger(INFO, "the image at {0} was marked NSFW, skiping".format(child['data']['id']))
            continue
        for f in filter(_filter_func(child), srt_handlers):
            try:
                possible = f(conf, child), child['data']['id']
                #check that it is a legal ending
                if possible[0].split('.')[-1] in conf.picture_endings:
                    return possible
                else:
                    conf.logger(INFO,"the image at {0} was of an illegal file type, skipping".format(child['data']['id']))
                    #the handler worked but is the wrong file-type, next picture
                    break
            except Unsuitable:
                # there is something wrong with the picture (i.e. wrong size) so skip it
                break
            except Unsuccessful:
                # this handler was not made for this picture, try again
                continue
        conf.logger(INFO, "could not find a suitable background within {0}.".format(child['data']['id']))
    conf.logger(WARNING, "none of the possibilities could be used")
    raise Failed("could not get a suitable url")

def _handler_cmp(a, b):
    if not hasattr(a, 'priority'): a.priority = 100
    if not hasattr(b, 'priority'): b.priority = 100
    if a.priority == b.priority:
        if hasattr(a, '_runtime_check'):
            return 1 # we want the runtime check to be last
        else:
            return -1
    elif a.priority > b.priority:
        return -1
    else:
        return 1

def _filter_func(child):
    def _(f):
        if hasattr(f, 'acceptable'):
            return f.acceptable(child)
        else:
            return True
    return _
