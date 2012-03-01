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

from os import access, R_OK
from .confparser import confToDict 
from ..loggers import WARNING

__all__ = ['parse_cfg_file']

UNKNOWN_ARG_FORMAT = "The argument {0}, from file {1} was not recognized."


def parse_cfg_file(nspace, f_name):
    if not os.access(f_name, R_OK):
        nspace.messages.append("there is no config file at {}".format(f_name))
        return nspace
    conf = confToDict(f_name)
    return nspace

