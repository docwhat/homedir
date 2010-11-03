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

## TODO: unmergeSubDir -- turn directories back to symlinks or delete.

import os, sys, traceback
from handle import warn
from pathname import Pathname

__all__ = ('NotPackageError', 'ConflictError', 'Package',
           'CONTROLDIR', 'CONTROLFILENAME', 'OLD_CONTROLFILENAME', 'PKG_VERSION' )

CONTROLDIR = ".homedir"
CONTROLFILENAME = "control"
OLD_CONTROLFILENAME = ".homedir.control"
PKG_VERSION = 1
IGNORE_DIRS=('.svn','CVS','RCS','.git')

# Error Classes
class NotPackageError(StandardError):
    "This is not a package."
class ConflictError(StandardError):
    "There has been a conflict with another package."
    src = None
    dst = None
    def __init__(self,src,dst,*args):
        self.src = src
        self.dst = dst
        StandardError.__init__(self,*args)

    def __str__(self):
        src = self.src
        dst = self.dst
        return "The file %(dst)s prevents linking %(src)s" % locals()

class Package(object):
    """HomeDir Package class.

    """
    package = None
    priority = None
    maintainer = None
    standards_version = None
    description = None
    dirs = None
    mkdirs = None

    package_location = None
    src_dirs = None
    src_mkdirs = None

    conflict_resolver = None

    _attributes = ('package','priority','maintainer','depends',
                   'standards-version','description','dirs','mkdirs',
                   'ubuntu-packages')

    @apply
    def name():
        def fget(self):
            return self.package
        return property(**locals())

    def __init__(self, directory, catalog):
        self.catalog = catalog
        self.package_location = directory = Pathname(directory).realpath()
        self._depends = set()

        # Find the control directory, supporting the old name.
        control = directory + CONTROLDIR + CONTROLFILENAME
        if not control.isfile():
            control = directory + OLD_CONTROLFILENAME

        if not control.isfile():
            raise NotPackageError("No control file")

        self._parse(control)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__,
                            self.package)

    def __eq__(self,other):
        if isinstance(other,self.__class__):
            return self.package_location == other.package_location
        elif isinstance(other,str):
            return self.package == other
        else:
            raise TypeError( "%s cannot be compared to %s" % (
                self.__class__, type(other)))

    @apply
    def depends():
        def fget(self):
            return self.catalog.find(*self._depends)
        return property(**locals())

    def _parse(self,control):
        curr = None
        fp = file(unicode(control),'r')
        num = 0
        for line in fp.readlines():
            num += 1
            line = line.rstrip()
            sline = line.strip()
            # Empty line, interrupts a list
            if sline == '':
                curr = None
                continue
            # Comments are ignored
            if sline.startswith('#') or sline.startswith(';'):
                continue
            if curr and \
               ( line.startswith(' ') or line.startswith('\t') ):
                self._attribute_append(curr,line,control,num)
                continue

            try:
                # Try to see if it's an attribute
                parts = line.split(':',1)
                if len(parts) > 1:
                    attribute,value = parts
                    value.rstrip()
                else:
                    attribute = parts[0]
                    value = None
            except ValueError:
                print >> sys.stderr, "Invalid control file: %s:%d" % (control,num)
                sys.exit(1)

            if attribute not in self._attributes:
                print >> sys.stderr, "Invalid attribute '%s' in control file:\n\t%s:%d" % (
                    attribute,control,num)
                sys.exit(1)
            self._attribute_set(attribute,value,control,num)
            curr = attribute

        # Validate the mkdirs -- must be in dirs
        if self.mkdirs and self.dirs:
            for mkdir in self.mkdirs:
                if mkdir not in self.dirs:
                    print >> sys.stderr, \
                          "Invalid mkdir: '%s' isn't marked as a dir" % \
                          mkdir
                    sys.exit(1)

        # List of real locations for the dirs in src
        src_dirs = self.src_dirs = []
        if self.dirs:
            for directory in self.dirs:
                src_dirs.append(self.package_location + directory)

        # List of real locations of diretories to make in src
        src_mkdirs = self.src_mkdirs = []
        if self.mkdirs:
            for mkdir in self.mkdirs:
                src_mkdirs.append(self.package_location + mkdir)

    def _attribute_set(self,attr,val,file,linenum):
        "Internal Method to set an attribute"
        if attr in ('mkdirs','dirs'):
            if val.strip():
                print >> sys.stderr, "%s start on the next line: %s:%d" % (
                    attr, file,linenum)
                sys.exit(1)
            setattr(self,attr, [])
        elif attr == "depends":
            self._depends = set([x.strip() for x in val.split(',') if x])
        elif attr == 'standards-version':
            val = int(val)
            if val != PKG_VERSION:
                raise NotPackageError("Invalid control file version: %s" % file)
            self.standard_version = val
        elif attr in self._attributes:
            setattr( self, attr, val.strip() )
        else:
            raise AssertionError("Invalid Attribute %s: %s:%d" % (attr,file,linenum))

    def _attribute_append(self,attr,val,file,linenum):
        "Internal Method to correct append to an attribute"
        if attr in ('mkdirs','dirs'):
            getattr(self,attr).append(val.strip())
        elif attr == "depends":
            self._depends.update(set([x.strip() for x in val.split(',')]))
        elif attr == 'standards-version':
            raise AssertionError("Can't append %s" % attr)
        elif attr in self._attributes:
            setattr(self, attr, getattr(self,attr) + '\n' + val.rstrip())
        else:
            raise AssertionError("Invalid Attribute %s: %s:%d" % (attr,file,linenum))

    def _resolveConflict(self,src,dst):
        raise "NARF"
        if self.conflict_resolver:
            return self.conflict_resolver(src,dst)
        else:
            raise ConflictError(src=src, dst=dst)

    def normalize(self, catalog):
        self.depends = catalog.find(*self.depends)

    def prettyPrint(self):
        "Pretty Print the package"
        def strify(o):
            if o is None:
                return 'none'
            if isinstance(o, self.__class__):
                return o.package
            if isinstance(o, list):
                return ', '.join([strify(x) for x in o])
            return unicode(o)
        print self.package
        print "  priority:          %s"  % self.priority
        print "  maintainer:        %s"  % self.maintainer
        print "  standards-version: %s"  % self.standards_version
        print "  description:       %s"  % self.description.split('\n')[0]
        print "  dirs:              %s"  % strify(self.dirs)
        print "  mkdirs:            %s"  % strify(self.mkdirs)
        print "  package-location:  %s"  % strify(self.package_location)
        #print "  src-dirs:          %s"  % strify(self.src_dirs)
        #print "  src-mkdirs:        %s"  % strify(self.src_mkdirs)
        print "  depends:           %s"  % strify(self.depends)

    def unsymlink(self,file):
        "Helper method to remove a symlink and only symlinks"
        assert(isinstance(file,Pathname))
        if file.islink():
            file.unlink()
        elif file.exists():
            raise AssertionError("%s is not a symlink" % file)
        # else: It must not exist!

    def symlink(self, src, dst):
        "Perform a relative symlink"

        assert(isinstance(src, Pathname))
        assert(isinstance(dst, Pathname))
        src.relative_path_from(dst.dirname()).symlink(dst)

    def short_description():
        doc = "Just the first line of the description"
        def fget(self):
            desc = self.description
            if desc:
                return desc.split('\n')[0]
            else:
                return "No Description"
        fset = fdel = None
        return locals()
    short_description = property(**short_description())

    def fromSubdir(cls,directory):
        "Classmethod: Create a package from a subdirectory"
        directory = Pathname(directory)
        if (directory + CONTROLDIR + CONTROLFILENAME).exists() or \
           (directory + OLD_CONTROLFILENAME).exists():
            return cls(directory)
        updir = directory.dirname()
        if updir != os.sep:
            return cls.fromSubdir(updir)
        else:
            return None
    fromSubdir = classmethod(fromSubdir)


    def merge(self,dest,src=None):
        "Merge the package into dest"
        ignore_control = src is None
        if src is None:
            src = self.package_location
        assert(isinstance(src, Pathname))
        assert(isinstance(dest, Pathname))
        dest = dest.realpath()
        for content in src.listdir():
            if content in IGNORE_DIRS:
                continue
            if ignore_control and (content == CONTROLDIR or content == OLD_CONTROLFILENAME):
                continue
            if (src + content).isdir():
                self.mergeSubDir(src,dest,content)
            else:
                self.mergeNonDir(src,dest,content)

    def isWithinLocation(self, path):
        "Returns true if path is within our package location"
        assert(isinstance(path, Pathname))
        return path.is_subdir_of(self.package_location)

    def mergeSubDir(self,src,dest,content):
        "Merge the subdirectory content from src to dest"
        assert(isinstance(src, Pathname))
        assert(isinstance(dest, Pathname))
        destpath = dest + content
        srcpath = src + content
        if srcpath not in self.src_dirs:
            return # We skip stuff not in directories
        if srcpath in self.src_mkdirs and not destpath.exists():
            destpath.mkdir()
        if destpath.islink():
            linkpath = destpath.realpath()
            if self.isWithinLocation(linkpath):
                # This is fine.  The link is actually one of ours.
                # Nuke it to make sure it's correct
                self.unsymlink(destpath)
                self.symlink(srcpath,destpath)
            elif destpath.exists():
                if linkpath == srcpath:
                    warn( "%s already points to %s" % (destpath,
                                                       srcpath) )
                    return
                if srcpath.isdir():
                    other = self.__class__.fromSubdir(linkpath)
                    if not other:
                        if self._resolveConflict(src=srcpath,
                                                 dst=destpath):
                            # Retry after the resolve
                            self.mergeSubDir(src,dest,content)
                    else:
                        self.unsymlink(destpath)
                        destpath.mkdir()
                        self.merge(src=srcpath,dest=destpath)
                        other.merge(src=linkpath,dest=destpath)
                else:
                    raise AssertionError("Untested path")
                    self._resolveConflict(src=srcpath, dst=destpath)
            else:
                if self._resolveConflict(src=srcpath, dst=destpath):
                    self.unsymlink(destpath)
                    self.symlink(srcpath,destpath)
        elif destpath.exists():
            if destpath.isdir():
                self.merge(src=srcpath,dest=destpath)
            else:
                if self._resolveConflict(src=srcpath, dst=destpath):
                    self.symlink(srcpath,destpath)
                # else keep on trucking.
        else:
            self.symlink(srcpath,destpath)


    def mergeNonDir(self, src, dest, content):
        assert(isinstance(src, Pathname))
        assert(isinstance(dest, Pathname))

        # src is the stow directory we're merging from
        srcpath = src + content
        # dest is the target directory that we are dropping
        # symlinks into
        destpath = dest + content

        if destpath.islink():
            linkpath = destpath.realpath()
            if linkpath.exists():
                if self.isWithinLocation(linkpath):
                    warn( "%s already points to %s" % (destpath,
                                                       srcpath) )
                else:
                    if self._resolveConflict(src=srcpath,
                                             dst=destpath):
                        self.symlink(srcpath,destpath)
            else:
                # It's a broken symlink and safe to nuke it (yes?)
                self.unsymlink(destpath)
                self.symlink(srcpath,destpath)
        elif destpath.exists():
            if self._resolveConflict(src=srcpath, dst=destpath):
                self.symlink(srcpath,destpath)
            # otherwise, we're skipping the conflict
        else:
            self.symlink(srcpath,destpath)

    def unmerge(self,dest,only_dirs=None):
        "Unmerge the package from dest"

        assert(isinstance(dest,Pathname))
        dest = dest.realpath()

        # We only check these dirs
        if only_dirs is None:
            only_dirs = [dest]
            if self.dirs:
                for directory in self.dirs:
                    only_dirs.append(dest + directory)

        elif dest not in only_dirs:
            # It's not prunable, don't worry about it.
            return False

        if dest == self.package_location:
            return False # It's not empty

        is_empty = True
        for content in dest.listdir():
            destpath = dest + content
            if destpath.islink():
                linktarget = destpath.realpath()
                if self.isWithinLocation(linktarget):
                    self.unsymlink(destpath)
                else:
                    is_empty = False
            elif destpath.isdir():
                is_destpath_empty = self.unmerge(destpath, only_dirs)
                is_empty = is_destpath_empty and is_empty
            else:
                is_empty = False

        if is_empty:
            try:
                dest.rmdir()
            except:
                tb = traceback.format_exception( *sys.exc_info() )
                print >> sys.stderr, "Unable to remove directory %s:\n %s" % (
                    dest,tb[-1].rstrip())

        return is_empty

    def install(self,dest,src=None):
        "Install the package"
        _src = src
        if _src is None:
            _src = self.package_location
        else:
            _src = Pathname(_src)
        dest = Pathname(dest)
        preflight = _src + CONTROLDIR + 'pre-install'
        if preflight.access(os.X_OK):
            os.system(preflight)

        self.merge(dest,src)

        postflight = _src + CONTROLDIR + 'post-install'
        if postflight.access(os.X_OK):
            os.system(postflight)

    def remove(self,dest,src=None):
        "Remove the package"
        _src = src
        if _src is None:
            _src = self.package_location
        else:
            _src = Pathname(_src)
        dest = Pathname(dest)

        preflight = _src + CONTROLDIR + 'pre-remove'
        if preflight.access(os.X_OK):
            os.system(preflight)

        self.unmerge(dest,src)

        postflight = _src + CONTROLDIR + 'post-remove'
        if postflight.access(os.X_OK):
            os.system(postflight)

# vim: set sw=4 ts=4 expandtab
