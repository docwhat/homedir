# -*- coding: utf-8 -*-
"""
This is a package management system designed to work around packages
for the homedirectory.  The code is based upon ideas from GNU Stow.

HomeDir - manage the installation of packages for a user's homedir
Copyright (C) 2004-2012 by Christian Höltje

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
    ##
    # Arguments:
    # * debug -- Turn on debugging in the catalog code.
    # * mock_packages -- A hash of mock packages for testing purposes.
    def __init__(self, debug=False, mock_packages=None):
        self.packages = packages = {}
        self.debug    = debug
        if mock_packages is not None:
            self.packages = mock_packages
        else:
            top = os.path.expanduser("~/.homedir/packages")

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
            deps = package.depends
            for dep in deps:
                found.add(dep)
                self.findDependencies(dep, found=found)

        return found

    def findReverseDependencies(self, *packages, **kwargs):
        """
        Returns all reverse dependencies for the list of packages.
        """

        found = kwargs.get('found', set())
        packages = set([self.packages.get(x,x) for x in packages])

        for parent in self.packages.values():
            for dependent in packages:
                if dependent in parent.depends:
                    found.add(parent)
                    # Add all parent packages too.
                    self.findReverseDependencies(parent, found=found)

        return found

if __name__ == "__main__":
    import unittest

    class TestCatalog(unittest.TestCase):
        class MockPackage:
            def __init__(self, name, depends_on=None):
                if depends_on is None:
                    depends_on = []
                self.depends = depends_on
                self.name = name
            def __repr__(self):
                return "<MockPackage name=%r>" % self.name

        def test_findDependencies(self):
            # Setup
            mock_grandchild = self.MockPackage("grandchild")
            mock_dependent  = self.MockPackage("dependent", depends_on=[mock_grandchild])
            mock_parent     = self.MockPackage("parent", depends_on=[mock_dependent])
            mock_packages = {'parent': mock_parent,
                             'dependent': mock_dependent,
                             'grandchild': mock_grandchild,
                             }
            catalog = Catalog(debug=True, mock_packages=mock_packages)

            # Activity
            dependents = catalog.findDependencies(mock_parent)

            # Verify
            expected = set([mock_dependent, mock_grandchild])
            self.assertEqual(expected, dependents)

        def test_findReverseDependencies(self):
            # Setup
            mock_dependent   = self.MockPackage("dependent")
            mock_parent      = self.MockPackage("parent", depends_on=[mock_dependent])
            mock_grandparent = self.MockPackage("grandparent", depends_on=[mock_parent])
            mock_packages = {
                'parent':      mock_parent,
                'dependent':   mock_dependent,
                'grandparent': mock_grandparent,
            }
            catalog = Catalog(debug=True, mock_packages=mock_packages)

            # Activity
            parents = catalog.findReverseDependencies(mock_dependent)

            # Verify
            expected = set([mock_parent, mock_grandparent])
            self.assertEqual(expected, parents, "Expected %r items, got %r" % (expected, parents))

    unittest.main()
#    cat = Catalog()
#    pkgs = cat.packages.values()
#    pkgs.sort()
#    for pkg in pkgs:
#        print "------------------------"
#        #pkg.prettyPrint()
#        print pkg.name
#        print cat.findDependencies(pkg)
#
# EOF
