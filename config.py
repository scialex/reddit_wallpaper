#!/usr/bin/python

#this file will parse the config files and the cli input for the application
import argparse
from collections import namedtuple

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
    parser.add_argument('--config', action = 'store',
		        nargs = 1,
			dest = 'cfg',
			help = 'use the given config file instead of the default ones') 
    parser.add_argument('--debug', action = 'store_true',
		        default = False,
		        help = "print out debug information")
    return parser.parse_args(namespace = nspace)

def parse_config_files(files = CONFIG_LOC):
    pass

print vars(parse_cmd_line())
