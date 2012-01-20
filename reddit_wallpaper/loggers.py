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
#this file is part of the Reddit Background Updater
import sys
try:
    import syslog
    _has_syslog = True
except Exception:
    _has_syslog = False

EMERGENCY = 0
ALERT     = 1
CRITICAL  = 2
ERROR     = 3
WARNING   = 4
NOTICE    = 5
INFO      = 6
DEBUG     = 7

LEVELS = {DEBUG     : 'debug',
          INFO      : 'info',
          NOTICE    : 'notice',
          WARNING   : 'warning',
          ERROR     : 'error',
          CRITICAL  : 'critical',
          ALERT     : 'alert',
          EMERGENCY : 'emergency'}

def printer_gen(name, min_lvl):
    """
    Takes in a name and a syslog logging leven and returns a function that
    takes in a severity level and a message and prints the message to the
    std-out if the severity is higher than the min level given
    """
    def printer(lvl, msg):
        if lvl <= min_lvl:
            print LEVELS[lvl] + ": " + msg
        return
    return printer

def syslog_gen(name, min_lvl):
    """
    Takes in a name and a syslog logginv level and returns a function that takes
    in a severity level and a message and sends the message to the syslogd if it
    is available
    """
    if not _has_syslog:
        return lambda a, b: None
    def logit(lvl, msg):
        syslog.openlog(name)
        syslog.setlogmask(syslog.LOG_UPTO(min_lvl))
        syslog.syslog(''.join(('(', LEVELS[lvl], ') ', msg)))
        syslog.closelog()
    return logit

quiet_gen = syslog_gen
def normal_gen(name, min_lvl):
    sl = syslog_gen (name, min_lvl)
    pl = printer_gen(name, min_lvl)
    def bth(lvl, msg):
        sl(lvl, msg)
        pl(lvl, msg)
    return bth

quiet  = quiet_gen(sys.argv[0],  WARNING)
normal = normal_gen(sys.argv[0], WARNING)
debug  = normal_gen(sys.argv[0], DEBUG)
