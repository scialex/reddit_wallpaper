# Copyright 2012, Alex Light.
#
# This file is part of Reddit background updater (RBU).
#
#__package__ = 'reddit_wallpaper.websites'

from .handlers import default_handlers
from .._exceptions import *
from itertools import ifilter
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
    srt_handlers = sorted(handlers, _handler_cmp)
    for child in data[0:conf.num_tries]:
        conf.logger(INFO, "trying reddit post {0}, is a link to {1}.".format(child['data']['id'],
                                                                             child['data']['url']))
        if conf.allow_nsfw is False and child["data"]["over_18"] is True:
            conf.logger(INFO, "the image at {0} was marked NSFW, skiping".format(child['data']['id']))
            continue
        try:
            def _filter_func(f):
                if hasattr(f, 'acceptable'):
                    return f.acceptable(child)
                else:
                    return True
            for f in ifilter(_filter_func, sorted(handlers, _handler_cmp)):
                return f(conf, child), child['data']['id']
        except Unsuitable:
            continue
    conf.logger(WARNING, "none of the possibilities could be used")
    raise Failed("could not get a suitable url")
