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

import os, sys
from homedir.package import *

class MissingPackageError(StandardError): pass

def scanPackages(options):
    """Scan all the package directories, building up a list of packages
    """
    top = os.path.expanduser("~/.homedir/packages")

    packages = options.packages = {}

    def walker(arg, dirname, fnames):
        try:
            package = Package(dirname)
            packages[package.package] = package
            while len(fnames) > 0:
                del fnames[0]
        except NotPackageError,err:
            for i in range(len(fnames)-1, 0-1, -1):
                fname = fnames[i]
                if fname.startswith('.'):
                    del fnames[i]

    os.path.walk(top, walker, None)

    return packages

def lookUp(options,*names):
    """Look up one or more packages; one per string in names"""
    packages = []
    bad = []
    for name in names:
        if isinstance(name,Package) and \
           options.packages.has_key(name.package):
            if name not in packages:
                packages.append(name)
        elif options.packages.has_key(name):
            p = options.packages[name]
            if p not in packages:
                packages.append(p)
        else:
            bad.append(name)
    if bad:
        raise MissingPackageError("Unknown packages: %s" % (",".join(map(str,bad))))
    return packages

def lookUpOne(options,name):
    "look up just one name"
    results = lookUp(options,name)
    if results:
        return results[0]
    else:
        return None

def scanDepends(options):
    for package in options.packages.values():
        if package.depends is None:
            continue
        print "NARF %s: %r" % (package.package, package.depends)
        try:
            package.depends = [lookUpOne(options,x) for x in package.depends]
        except MissingPackageError, err:
            if options.debug:
                raise AssertionError( "Bad Packages: %s" % ",".join(map(str,bad)))
            print >> sys.stderr, "In the package '%s': %s" % (package.package, err)
            sys.exit(1)

