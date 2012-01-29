#!/usr/bin/python
#
# Copyright (C) 2011
#
# Douglas Schilling Landgraf <dougsland@redhat.com>
#
# python-confparser - A KISS python module to parse *nix config files
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301
# USA
#
# This was switched from the LGPL 2.1 to GPL 3 according to section 3 of the
# LGPL. This version has been striped of all file editing capabilities.
#
# original: https://github.com/dougsland/python-confparser/

import sys

__version__    = "1.0.1.1"

def getConfValue(pathFile, confName):

    confValue = ""
    found = -1

    try:
        FILE = open(pathFile).readlines()
    except IOError as e:
        print "cannot locate configuration file: %s" %pathFile
        raise

    for line in [l.strip() for l in FILE]:
        if not line:
            continue

        ret = line.find(confName)
        if ret != -1:
            # configuration commented? return value is #
            if line[0] == "#":
                confValue = "confCommented"
            else:
                sizeString = len(line)
                indexEqual = line.index('=')
                indexEqual += 1 # Get next caracter from =
                for i in range(indexEqual, sizeString):
                    if (line[i] == "\"") or (line[i] == " "):
                        continue
                    confValue += line[i]
                    # we have found the conf - raising flag found = 0 (OK)
                    found = 0

    # The configuration not found? return the string "confNotFound"
    if (confValue == "" and (found == -1)):
        confValue = "confNotFound"

    return confValue

def confToDict(pathFile):

    var = {}

    try:
        FILE = open(pathFile, 'r+')
    except IOError as e:
        reason = e.args[1]
        print "cannot find configuration file: {0}\n{1}".format(pathFile, reason)
        sys.exit(-1)

    while True:

        # cleaning variables
        cleanConfValue = ""
        cleanConfName  = ""
        confName       = ""
        confValue      = ""
        confStatus     = ""
        typeAttribute  = "NoAttr"
        quoteCount     = 0

        line = FILE.readline()
        ret = line.find("=")
        if ret != -1:
            if line[0] == "#":
                confStatus = "commented"
            else:
                confStatus = "activated"

            conf = line.split('=')

            # conf[0] = confName - conf[1] = confValue
            confName  = conf[0]
            confValue = conf[1]

            # Cleaning the confName
            sizeString = len(conf[0])
            for i in range(0, sizeString):
                if (confName[i] == "#") or (confName[i] == " ") or (confName[i] == "\n"):
                    continue
                cleanConfName += confName[i]


            # Cleaning the confValue - removing " or spaces
            sizeString = len(conf[1])
            for i in range(0, sizeString):
                if (confValue[i] == "\""):
                    typeAttribute = "string"
                    quoteCount += 1
                    continue

                # removing space from numbers
                if not typeAttribute == "string":
                    if (confValue[i] == " ") or (confValue[i] == "\n"):
                        continue

                    if confValue[i] == "#":
                        break
                else:
                    if confValue[i] == "\n":
                        continue

                if quoteCount == 2:
                    quotCount = 0
                    break

                cleanConfValue += confValue[i]

            if typeAttribute == "NoAttr":
                typeAttribute = "no string"

            # appending to the dict
            u = {cleanConfName:cleanConfValue, (cleanConfName + '_status'):confStatus,
                    (cleanConfName + '_type'):typeAttribute}

            #print u
            var.update(u)

        # len = 0 - No more lines to read (EOF)
        if len(line) == 0:
            break

    FILE.close()

    return var
