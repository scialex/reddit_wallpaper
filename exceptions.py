# Copyright 2012, Alex Light.
#
# This file is part of Reddit background updater (RBU).

"""Keep all the signaling exceptions together in one place."""

class Failed(Exception):
    """
    This is used when there is a failure and it was not compleatly
    unexpected but was totally fatal (i.e. no internet)
    """
    pass

class Unsuccessful(Exception):
    """
    This is used when there is a failure but it is not fatal
    """
    pass

class Unsuitable(Exception):
    """
    this is thrown when there is a normal case where a condition is wrong.
    for example a picture is too big, etc.
    """
    pass
