# Copyright 2012, Alex Light.
#
# This file is part of Reddit background updater (RBU).
#
import re
import imagefacts
import json
from urllib2 import urlopen, HTTPError
from . import check_size
from .exceptions import Unsuitable
from ..loggers import DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY
from .decorators import *

IMGUR_JSON_FORMAT = "http://api.imgur.com/2/image/{0}.json"#{0} is the imgur photo id hash
FLICKR_JSON_FORMAT = 'http://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=eaf4581fb8d0655b0a314d13ab54ef46&photo_id={0}&format=json&nojsoncallback=1'#{0} is the flickr photo-id number
DEVIANT_ART_JSON_FORMAT = 'http://backend.deviantart.com/oembed?url={0}'#{0} is the url of the deviantart page

def _direct_link_check(endings):
    """
    takes in the list of picture endings and creates a regex that matches if
    the url ends with any of them. returns the search function of this regex
    object
    """
    re.compile('^https?.*\.({0})$'.format('|'.join(endings)))
    return re.search

@priority(100)
@requires_runtime_checking(_direct_link_check(conf.picture_endings))
def direct_link_handler(conf, child):
    """
    this function will try to figure out the size of a direct image link.
    """
    url = child['data']['url']
    try:
	if conf.size_limit is not None:
	    size = imagefacts.facts(url)[1:]
	else:
	    size = None 
    except Exception as e:
	conf.logger(WARNING,
		    "something happened while trying to retrieve the image at {0} in order to determine its size. type of exception was {1} and reason given was {2}".format(url, type(e), e.args))
	raise excpetions.Unsuitable() 
    if not check_size(conf, size):
	conf.logger(DEBUG,
		    "the image at {0} was not the right size".format(url))
	raise excpetions.Unsuitable() 
    conf.logger(INFO, 'found {0}, link was direct to a non_imgur site'.format(url))
    return url

@priority(100)
@requires_domain('i.imgur.com')
def i_imgur_handler(conf, child):
    """
    this function will find the download link for this image as long
    as it is a link to imgur.com, it will just skip any albums
    """
    url = child['data']['url']
    if conf.size_limit is not None:
	try:
	    data = json.loads(urlopen(IMGUR_JSON_FORMAT.format(url.split('/')[-1][:5])).read())
	    conf.logger(DEBUG,
			"was able to retrieve the image metadata from imgur for image {0}".format(url))
	except HTTPError:
	    raise excpetions.Unsuitable() 
	if not check_size(conf,
			  (data["image"]["image"]["width"],
			   data["image"]["image"]["height"])):
	    conf.logger(DEBUG,
			"the image at {0} was not the right size".format(url))
	    raise Unsuitable()	
    conf.logger(INFO, 'found {0}, link was direct to i.imgur.com'.format(url))
    return url

@priority(100)
@requires_domain('flickr.com')
def flickr_handler(conf, child):
    url = child['data']['url']
    try:
	#the url splits into ['http:','','www.flickr,com','photos','username','photoid',etc]
	#                       0      1           2          3       4          *5*    etc
	photo_id = url.split('/')[5]
	conf.logger(DEBUG, 'flickr link found. url is {0}, photo_id determined to be {1}'.format(url, photo_id))
	data = json.loads(urlopen(FLICKR_JSON_FORMAT.format(photo_id)).read())
	if data['stat'] != 'ok':
	    conf.logger(WARNING, "got a failure response from the flickr api. status was given as {0}. message was given as {1}. skipping this link".format(data['stat'], data['message']))
            raise Unsuitable()	
	if data['sizes']['candownload'] == 0 and conf.respect_flickr_nodownload:
	    conf.logger(INFO, "The poster declined to allow downloading of his image and the configuration was set to respect his wishes")
            raise Unsuitable()	
	return choose_flickr_size(conf, data)
    except HTTPError as h:
	conf.logger(WARNING, "an HTTPError was caught, reason given was {0}. skipping this link".format(str(h)))
        raise Unsuitable()	

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
	conf.logger(DEBUG, "flickr did not have any link that was the right size")
	raise Unsuitable()
    else:
	conf.logger(DEBUG, 'chose size to be one labled {0}'.format(best['label']))
	return best['source'].replace('\\','')

@priority(100)
@requires_domain('imgur.com')
def imgur_handler(conf, child):
    url = child['data']['url']
    name = url.split('/')[-1]
    try:
	data = json.loads(urlopen(IMGUR_JSON_FORMAT.format(name)).read())
    except HTTPError:
	conf.logger(WARNING,
		    "was unable to use the imgur api to determine the size of the image at {0}, skiping".format(url))
	raise Unsuitable()
    #check if the size is right
    if not check_size(conf, (data["image"]["image"]["width"],
			     data["image"]["image"]["height"])):
	raise Unsuitable()
	
    link = data["image"]["links"]["original"]
    conf.logger(INFO, 'found {0}, link was not direct'.format(url))
    return link

@priority(100)
@requires_domain(re.compile("^.*\.?deviantart\.com$"))
def deviantart_handler(conf, child):
    url = child['data']['url']
    try: data = json.loads(urlopen(DEVIANT_ART_FORMAT.format(url)).read()) 
    except HTTPError as h:
	conf.logger(WARNING, "recieved an HTTPError when tried to use oembeded api to query deviantart url {0}. response was: {1}.".format(url, h))
	raise Unsuitable()
    if not check_size(conf, (data['width'],data['height'])):
	raise Unsuitable()
    return data['url'].replace('\\','')

default_handlers = [imgur_handler, 
		    flickr_handler,
		    direct_link_handler,
		    i_imgur_handler,
		    deviantart_handler]		    
