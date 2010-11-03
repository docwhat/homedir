# -*- coding: utf-8 -*-
"""
This is a package management system designed to work around packages
for the homedirectory.  The code is based upon ideas from GNU Stow.

HomeDir - manage the installation of packages for a user's homedir
Copyright (C) 2004-2010 by Christian Höltje

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

__all__ = ( 'warn_mode', 'warn', 'pluralize' )

# Warn mode helper
WARN = False

def warn_mode(mode):
    "Set the mode to true or false."
    WARN = bool(mode)

def warn(*msg):
    "Either prints a warning message or is a nop, depending on options"
    if WARN:
        print "WARN: %s" % " ".join(map(str,msg))

def pluralize(singular,plural,count):
    "Returns the correct form of a word, based on count"
    if count == 1:
        return singular
    elif count > 1 or count == 0:
        return plural
    else:
        raise AssertionError("Unable to pluralize")

