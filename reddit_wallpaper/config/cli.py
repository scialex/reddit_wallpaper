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

"""
This module contains the code nessecary to read and interpret the command line options and configuration passed
into this program
"""

import argparse

__all__ = ['parse_cmd_line', 'get_parser']

def parse_cmd_line(nspace):
    return get_parser().parse_args(namespace = nspace)

def get_parser():
    parser = argparse.ArgumentParser(description = "this will retrieve a background from some subreddit and set its top image link as the background")
    parser.add_argument('-o', '--output',"--save-file",
                        action = 'store',
                        type = str,
                        dest = 'save_file',
                        metavar = 'NAME',
                        help = "the file by which you want the downloaded file to be saved under. note all occurances of '@' are replaced by the reddit post id number of the reddit submission, this will be unique to each file. if you do not use @ at all in the name be sure that this is set to overwrite already saved files")
    ovrwrt = parser.add_mutually_exclusive_group()
    ovrwrt.add_argument('--no-overwrite', action = 'store_false',
                        help = "do not overwrite any preexisting image files if the name is the same, this is enabled by default",
                        dest = "overwrite")
    ovrwrt.add_argument('--overwrite', action = 'store_true',
                        help = "redownload and overwrite any files bearing the same name as the one being downloaded, this is disabled by default",
                        dest = "overwrite")
    parser.add_argument("--endings", type = str,
                        action = 'store',
                        nargs = '+',
                        help = "the file types to accept for download")
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
    size.add_argument("--min",
                      type = n_or_none,
                      nargs = 2,
                      metavar = ('MIN_X', 'MIN_Y'),
                      help = "this specifices the minimum size of the image. Each argument must be either a positive non-zero number or the word 'none'")
    size.add_argument("--max",
                      type = n_or_none,
                      nargs = 2,
                      metavar = ("MAX_X", 'MAX_Y'),
                      help = "this specifices the maximum size of the image. Each argument must be either a positive non-zero number or the word 'none'")
    parser.add_argument('subreddit', nargs = '*', type = str,
                        default = argparse.SUPPRESS,
                        help = "the subreddits to check for images")
    nsfwallow = parser.add_mutually_exclusive_group()
    nsfwallow.add_argument("-N","--allow-nsfw", action = 'store_true',
                           dest = "allow_nsfw",
                           help = "allow nsfw content to be downloaded")
    nsfwallow.add_argument('-n','--no-nsfw', action = 'store_false',
                           dest = 'allow_nsfw',
                           help = "do not download any content marked nsfw")
    parser.add_argument('-t','--tries', type = n_or_none,
                        action = 'store',
                        metavar = 'number',
                        dest = 'num_tries',
                        help = "this specifies the number of posts to check before giving up on finding a good match. if the value is 'none', or this flag is not used, it will test all the posts it is given for a suitable image")
    sorttype = parser.add_argument_group('Sort Type',
                                         "Select the section of the subreddit to use for sorting. NB if more than one of these switches are present the result is undefined.")
    sorttype.add_argument('--hot', action = 'store_const',
                          const = '',
                          dest = 'sort_type',
                          help = "The default. Use the 'What's Hot' section of the subreddit")
    sorttype.add_argument('--new', action = 'store_const',
                          const = 'new/?sort=new',
                          dest = 'sort_type',
                          help = "Use the 'New' section of the subreddit")
    sorttype.add_argument('--controversial', action = 'store_const',
                          const = 'controversial/',
                          dest = 'sort_type',
                          help = "Use the 'Controversial' section of the subreddit")
    sorttype.add_argument('--top', action = 'store_const',
                          const = 'top/',
                          dest = 'sort_type',
                          help = "Use the 'Top' section of the subreddit")
    flickr_dl = parser.add_mutually_exclusive_group()
    flickr_dl.add_argument('--respect-flickr-download-flag',
                                 action = 'store_true',
                                 dest = 'respect_flickr_nodownload',
                                 help = "respect the wishes of the poster of images hosted on Flickr, only downloading them if the poster has enabled it, This is activated by default.")
    flickr_dl.add_argument('--ignore-flickr-download-flag',
                                 action = 'store_false',
                                 dest = 'respect_flickr_nodownload',
                                 help = "Ignore the no download flag on images stored on flikr, downloading them even if the poster has disabled downloads.")
#    parser.add_argument('--config', action = 'store',
#                        nargs = 1,
#                        dest = 'cfg',
#                        help = 'use the given config file instead of the default ones')
    prnts = parser.add_argument_group("Debug info", "these control how much information is printed onto the screen and into the logs. NB if more than one of these switches is present the result is undefined")
    prnts.add_argument('--debug', action = 'store_const',
                       dest = 'logger',
                       const = 'debug',
                       help = "print out debug information")
    prnts.add_argument('--quiet', action = 'store_const',
                       dest = 'logger',
                       const = 'quiet',
                       help = "do not print out status info")
    return parser


