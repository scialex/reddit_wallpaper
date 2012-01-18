# Copyright 2012, Alex Light.
#
# This file is part of Reddit background updater (RBU).
#

from PIL import Image
from StringIO import StringIO
from urllib2 import urlopen

def get_size_directly(url):
    return Image.open(StringIO(urlopen(url).read())).size

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
