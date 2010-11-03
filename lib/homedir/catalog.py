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
from package import *

class MissingPackageError(StandardError): pass

class Catalog:
    def __init__(self, debug=False):
        top = os.path.expanduser("~/.homedir/packages")
        self.packages = packages = {}
        self.debug    = debug

        ## Gather the packages.
        def walker(arg, dirname, fnames):
            try:
                package = Package(dirname, self)
                packages[package.package] = package
                while len(fnames) > 0:
                    del fnames[0]
            except NotPackageError,err:
                for i in range(len(fnames)-1, 0-1, -1):
                    fname = fnames[i]
                    if fname.startswith('.'):
                        del fnames[i]

        os.path.walk(top, walker, None)
        self.packages = packages

        ## ## Figure out dependencies.
        ## for package in packages.values():
        ##     if not package.depends:
        ##         continue
        ##     try:
        ##         package.depends = [self.findOne(x) for x in package.depends]
        ##     except MissingPackageError, err:
        ##         if self.debug:
        ##             raise AssertionError( "Bad Packages: %s" % ",".join(map(str,bad)))
        ##         print >> sys.stderr, "In the package '%s': %s" % (package.package, err)
        ##         sys.exit(1)

        ## ## Figure out reverse-dependencies.
        ## for depender in self.packages.values():
        ##     if depender.depends is None:
        ##         dependencies = []
        ##     else:
        ##         dependencies = depender.depends

        ##     for dependee in dependencies:
        ##         dependee = self.findOne(dependee)

        ##         if depender not in dependee.reverse_depends:
        ##             dependee.reverse_depends.append( depender )

## def buildPackageDepends(package,depends=None,ignore=None):
##     """ARGS:
##     package -- package to find dependencies for
##     depends -- packages that package depends on (needed for recursion)
##     ignore  -- packages to ignore (they are being taken care of elsewhere)

##     Returns depends"""
##     if depends is None:
##         depends = []
##     if package.depends:
##         for p in package.depends:
##             if p not in depends and \
##                (not ignore or p not in ignore):
##                 depends.append(p)
##             buildPackageDepends(p,depends,ignore)
##     return depends

## def buildDeps(options,*packages):
##     "Build up all the dependencies"

##     scanDepends(options)

##     allpkgs = []
##     for package in packages:
##         buildPackageDepends(package,allpkgs,ignore=packages)
##     return allpkgs

## def buildPackageReverseDepends(package,reverses=None,ignore=None):
##     if reverses is None:
##         reverses = []
##     if package.reverse_depends:
##         for p in package.reverse_depends:
##             if p not in reverses and \
##                (not ignore or p not in ignore):
##                 reverses.append(p)
##             buildPackageReverseDepends(p,reverses,ignore)
##     return reverses

## def buildRDeps(options,*packages):
##     "Build up all the reverse dependencies"

##     scanReverseDepends(options)

##     allpkgs = []
##     for package in packages:
##         buildPackageReverseDepends(package,allpkgs,ignore=packages)
##     return allpkgs

    def findOne(self, name):
        "Returns one package or None"
        res = self.find(name)
        if res:
            return tuple(res)[0]
        else:
            return None

    def find(self, *names):
        """Finds a package based on name.

        Returns a list of packages.
        """
        packages = set()
        bad = set()

        for name in names:
            if isinstance(name,Package) and \
               self.packages.has_key(name.package):
                packages.add(name)
            elif self.packages.has_key(name):
                packages.add(self.packages[name])
            else:
                bad.add(name)
        if bad:
            raise MissingPackageError("Unknown packages: %s" % (",".join(map(str,bad))))
        return packages


    def all(self):
        "Returns all packages"
        return self.packages.values()

    def findDependencies(self, *packages, **kwargs):
        "Returns all dependencies for the list of packages."

        found = kwargs.get('found', set())
        packages = set([self.packages.get(x,x) for x in packages])

        for package in packages:
            found.add(package)
            deps = package.depends
            if deps:
                for dep in deps:
                    found.add(dep)
                    found.update(self.findDependencies(dep, found=found))

        return found

    def findReverseDependencies(self, *packages, **kwargs):
        "Returns all reverse dependencies for the list of packages."

        found = kwargs.get('found', set())
        packages = set([self.packages.get(x,x) for x in packages])

        for package in self.packages.values():
            print "NARF %r" % package.depends
            if package in package.depends:
                found.add(package)

        for package in packages:
            found.add(package)
            deps = package.depends
            if deps:
                for dep in deps:
                    found.add(dep)
                    found.update(self.findDependencies(dep, found=found))

        return found

if __name__ == "__main__":
    cat = Catalog()
    pkgs = cat.packages.values()
    pkgs.sort()
    for pkg in pkgs:
        print "------------------------"
        #pkg.prettyPrint()
        print pkg.name
        print cat.findDependencies(pkg)

# EOF
