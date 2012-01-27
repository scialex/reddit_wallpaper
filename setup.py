#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(name = 'reddit_wallpaper',
      version = '0.4',
      description = 'updates the wallpaper from reddit',
      author = 'Alexander Light',
      packages = ['reddit_wallpaper',
                  'reddit_wallpaper.websites',
                  'reddit_wallpaper.platforms',
                  'reddit_wallpaper.config'],
      license = "GPL",
      requires = ['PIL','argparse'],
      entry_points = dict(console_scripts=['reddit-wallpaper=reddit_wallpaper:main']))

