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
#this file will parse the config files and the cli input for the application
import os
import argparse
from loggers import quiet, debug, normal
from collections import namedtuple

DEFAULT_LOG_LEVEL = 'debug'#change later

CONFIG_LOC = ['/etc/reddit_wallpaper','~/.reddit_wallpaper','./reddit_wallpaper']

configuration = namedtuple("configuration",
                           ["overwrite",
                            "num_tries",
                            "save_location",
			    "save_file",
                            "picture_endings",
                            "subreddit",
                            "allow_nsfw",
			    "size_limit",
			    "logger"])

size_limit = namedtuple("size_limit",
			["min_x","min_y",
			 "max_x","max_y"])

_loggers = {'quiet'  : quiet,
	    'debug'  : debug,
	    'normal' : normal}

def get_config():
    return convert_to_configuration(parse_cmd_line())

def convert_to_configuration(nspace):
    return configuration(overwrite = nspace.overwrite,
			 num_tries = nspace.num_tries,
			 save_location = os.path.expanduser(nspace.save_location),
			 save_file = nspace.save_file,
			 picture_endings = nspace.endings,
			 subreddit = '+'.join(nspace.subreddit) + '/' + nspace.sort_type,
			 allow_nsfw = nspace.allow_nsfw,
			 size_limit = None if [None, None] == nspace.min == nspace.max else size_limit(*(nspace.min + nspace.max)),
			 logger = _loggers[nspace.logger])
     
     
def parse_cmd_line(nspace = argparse.Namespace()):
    parser = argparse.ArgumentParser(description = "this will retrieve a background from some subreddit and set its top image link as the background")
    savloc = parser.add_argument_group("Save location","set the folder and file name for the downloaded pictures")
    savloc.add_argument("--save-location",
			action = 'store',
			nargs = 1,
			type = str,
			default = '~/.background_getter',
			metavar = "FOLDER",
			help = "the location where the downloaded file will be saved.")
    savloc.add_argument("--save-file",
			action = 'store',
			nargs = 1,
			default = '@',
			type = str,
			metavar = 'NAME',
			help = "the name by which you want the downloaded file to be saved under. note all occurances of '@' are replaced by the reddit post id number of the reddit submission, this will be unique to each file. if you do not use @ at all in the name be sure that this is set to overwrite already saved files")
    ovrwrt = parser.add_mutually_exclusive_group()
    ovrwrt.add_argument('-o','--no-overwrite', action = 'store_false',
			help = "do not overwrite any preexisting image files if the name is the same, this is enabled by default",
			dest = "overwrite",
			default = False)
    ovrwrt.add_argument('-O','--overwrite', action = 'store_true', 
			help = "redownload and overwrite any files bearing the same name as the one being downloaded, this is disabled by default",
			dest = "overwrite")
    size = parser.add_argument_group("Size limits",
				     "set the size limit for the images to be downloaded. Each value must be either a positive non-zero number or none if there is no limit for that variable")
    def n_or_none(s):
	if s == 'None' or s == 'none':
	    return None
	try:
	    v = int(s)
	    if v > 0:
		return v
	    else:
		raise Exception()
	except Exception:
	    msg = "{0} is not a valid input. The input shoudl either be a positive non-zero number or none".format(s)
	    raise argparse.ArgumentTypeError(msg)
    parser.add_argument("--endings", type = str,
			action = 'store',
			default = ['png', 'jpg', 'jpeg', 'gif'],
			nargs = '+',
			help = "the file type endings to accept for download")
    size.add_argument("--min",
		      type = n_or_none,
		      nargs = 2,
		      metavar = ('MIN_X', 'MIN_Y'),
		      default = [None, None],
		      help = "this specifices the minimum size of the image. Each argument must be either a positive non-zero number or the word 'none'")
    size.add_argument("--max",
		      type = n_or_none,
		      nargs = 2,
		      metavar = ("MAX_X", 'MAX_Y'),
		      default = [None, None],
		      help = "this specifices the maximum size of the image. Each argument must be either a positive non-zero number or the word 'none'")
    parser.add_argument('subreddit', nargs = '*', type = str, 
			default = ["wallpaper", "wallpapers"],
			help = "the subreddits to check for images")
    nsfwallow = parser.add_mutually_exclusive_group()
    nsfwallow.add_argument("-N","--allow-nsfw", action = 'store_true',
		           dest = "allow_nsfw",
			   help = "allow nsfw content to be downloaded")
    nsfwallow.add_argument('-n','--no-nsfw', action = 'store_false',
			   dest = 'allow_nsfw',
			   default = False,
			   help = "do not download any content marked nsfw")
    parser.add_argument('-t','--tries', type = n_or_none,
			action = 'store',
			default = None, 
			metavar = 'number',
			dest = 'num_tries',
			help = "this specifies the number of images to check before giving up on finding a good match. if the value is 'none' it will never give up trying to find an image it can use")
    sorter = parser.add_argument_group('Sort Type',
				       "Select the section of the subreddit to use for sorting") 
    sorttype = sorter.add_mutually_exclusive_group()
    sorttype.add_argument('--hot', action = 'store_const',
			  const = '', 
			  dest = 'sort_type',
			  default = '',
			  help = "The default. Use the 'What's Hot' section of the subreddit")
    sorttype.add_argument('--new', action = 'store_const',
			  const = 'new',
			  dest = 'sort_type',
			  help = "Use the 'New' section of the subreddit")
    sorttype.add_argument('--controversial', action = 'store_const',
			  const = 'controversial',
			  dest = 'sort_type',
			  help = "Use the 'Controversial' section of the subreddit")
    sorttype.add_argument('--top', action = 'store_const',
			  const = 'top',
			  dest = 'sort_type',
			  help = "Use the 'Top' section of the subreddit")
    parser.add_argument('--config', action = 'store',
		        nargs = 1,
			dest = 'cfg',
			help = 'use the given config file instead of the default ones') 
    printers = parser.add_argument_group("Debug info", "these control how much information is printed onto the screen and into the logs")
    prnts = printers.add_mutually_exclusive_group()
    prnts.add_argument('--debug', action = 'store_const',
		       default = DEFAULT_LOG_LEVEL,
		       dest = 'logger',
		       const = 'debug',
		       help = "print out debug information")
    prnts.add_argument('--quiet', action = 'store_const',
		       dest = 'logger',
		       const = 'quiet',
		       help = "do not print out status info")
    return parser.parse_args(namespace = nspace)

def parse_config_files(files = CONFIG_LOC):
    pass

print str(convert_to_configuration(parse_cmd_line())).replace(',',',\n             ')
