#!/usr/bin/env python

from setuptools import setup

setup(name = 'reddit_wallpaper',
      version = '0.4',
      description = 'updates the wallpaper from reddit',
      author = 'Alexander Light',
      packages = ['reddit_wallpaper', 'reddit_wallpaper.websites'],
      license = "GPL",
      entry_points = dict(console_scripts=['reddit-wallpaper=reddit_wallpaper:main']))

