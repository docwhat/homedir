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

__all__ = ('NotPackageError', 'ConflictError', 'Package',
           'CONTROLDIR', 'CONTROLFILENAME', 'OLD_CONTROLFILENAME' )

CONTROLDIR = ".homedir"
CONTROLFILENAME = "control"
OLD_CONTROLFILENAME = ".homedir.control"

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
    depends = None
    standards_version = None
    description = None
    dirs = None
    mkdirs = None

    package_location = None
    src_dirs = None
    src_mkdirs = None
    reverse_depends = None

    conflict_resolver = None

    _attributes = ('package','priority','maintainer','depends',
                   'standards-version','description','dirs','mkdirs',
                   'ubuntu-packages')

    def __init__(self, directory):
        self.package_location = os.path.realpath(directory)

        # Find the control directory, supporting the old name.
        control = os.path.join(directory,CONTROLDIR,CONTROLFILENAME)
        if not os.path.exists(control):
            control = os.path.join(directory,OLD_CONTROLFILENAME)

        if not os.path.exists(control):
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

    def _parse(self,control):
        curr = None
        fp = file(control,'r')
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
                src_dirs.append(os.path.join(self.package_location,directory))

        # List of real locations of diretories to make in src
        src_mkdirs = self.src_mkdirs = []
        if self.mkdirs:
            for mkdir in self.mkdirs:
                src_mkdirs.append(os.path.join(self.package_location,mkdir))

    def _attribute_set(self,attr,val,file,linenum):
        "Internal Method to set an attribute"
        if attr in ('mkdirs','dirs'):
            if val.strip():
                print >> sys.stderr, "%s start on the next line: %s:%d" % (
                    attr, file,linenum)
                sys.exit(1)
            setattr(self,attr, [])
        elif attr == "depends":
            d = self.depends = []
            d.extend( [x.strip() for x in val.split(',') if x] )
        elif attr == 'standards-version':
            val = int(val)
            if val != STANDARDSVERSION:
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
            d = self.depends
            d.extend( [x.strip() for x in val.split(',')] )
        elif attr == 'standards-version':
            raise AssertionError("Can't append %s" % attr)
        elif attr in self._attributes:
            setattr(self, attr, getattr(self,attr) + '\n' + val.rstrip())
        else:
            raise AssertionError("Invalid Attribute %s: %s:%d" % (attr,file,linenum))

    def _resolveConflict(self,src,dst):
        success = False
        if self.conflict_resolver:
            return self.conflict_resolver(src,dst)
        else:
            raise ConflictError(src=src, dst=dst)

    def unsymlink(self,file):
        "Helper method to remove a symlink and only symlinks"
        fdebug('%s.unsymlink' % self.package,
               {'file':file})
        if os.path.islink(file):
            os.unlink(file)
        elif os.path.exists(file):
            raise AssertionError("%s is not a symlink" % file)
        # else: It must not exist!

    def symlink(self, src, dest):
        "Perform a relative symlink"
        fdebug('%s.symlink' % self.package,
               {'src':src,
                'dest':dest})
        def split(path):
            "Splits apart the path into single directory components"
            parts = []
            parent, child = os.path.split(path)
            while child != '':
                parts.insert(0,child)
                parent, child = os.path.split(parent)
            return parts

        # To be user friendly, we'll keep the case here
        srclist = split(os.path.abspath(src))
        destlist = split(os.path.abspath(dest))

        while srclist[0] == destlist[0]:
            # Remove matching parts from the start of the path
            srclist.pop(0)
            destlist.pop(0)

        if len(destlist) >= 2:
            for i in range(0,len(destlist)-1):
                srclist.insert(0,os.pardir)

        os.symlink(os.path.join(*srclist),
                   dest)

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
        if os.path.exists(os.path.join(directory,CONTROLDIR,CONTROLFILENAME)) or \
               os.path.exists(os.path.join(directory,OLD_CONTROLFILENAME)):
            return cls(directory)
        updir = os.path.dirname(directory).rstrip(os.sep)
        if updir:
            return cls.fromSubdir(updir)
        else:
            return None
    fromSubdir = classmethod(fromSubdir)


    def merge(self,dest,src=None):
        "Merge the package into dest"
        fdebug('merge',locals())
        ignore_control = src is None
        if src is None:
            src = self.package_location
        dest = os.path.realpath(dest)
        for content in os.listdir(src):
            if content in IGNORE_DIRS:
                continue
            if ignore_control and (content == CONTROLDIR or content == OLD_CONTROLFILENAME):
                continue
            if os.path.isdir(os.path.join(src,content)):
                self.mergeSubDir(src,dest,content)
            else:
                self.mergeNonDir(src,dest,content)

    def isWithinLocation(self, path):
        "Returns true if path is within our package location"
        loc = "%s%s" % (self.package_location.rstrip(os.sep),os.sep)
        return path.startswith(loc)

    def mergeSubDir(self,src,dest,content):
        "Merge the subdirectory content from src to dest"
        fdebug('mergeSubDir',locals())
        destpath = os.path.join(dest,content)
        srcpath = os.path.join(src,content)
        if srcpath not in self.src_dirs:
            return # We skip stuff not in directories
        if srcpath in self.src_mkdirs and \
           not os.path.exists(destpath):
            os.mkdir(destpath)
        if os.path.islink( destpath ):
            linkpath = os.path.realpath( destpath )
            if self.isWithinLocation(linkpath):
                # This is fine.  The link is actually one of ours.
                # Nuke it to make sure it's correct
                self.unsymlink(destpath)
                self.symlink(srcpath,destpath)
            elif os.path.exists(destpath):
                if linkpath == srcpath:
                    warn( "%s already points to %s" % (destpath,
                                                       srcpath) )
                    return
                if os.path.isdir(srcpath):
                    other = self.__class__.fromSubdir(linkpath)
                    if not other:
                        if self._resolveConflict(src=srcpath,
                                                 dst=destpath):
                            # Retry after the resolve
                            self.mergeSubDir(src,dest,content)
                    else:
                        debug("%s splitting with %s" % (self, other))
                        self.unsymlink(destpath)
                        os.mkdir(destpath)
                        self.merge(src=srcpath,dest=destpath)
                        other.merge(src=linkpath,dest=destpath)
                else:
                    raise AssertionError("Untested path")
                    self._resolveConflict(src=srcpath, dst=destpath)
            else:
                if self._resolveConflict(src=srcpath, dst=destpath):
                    self.unsymlink(destpath)
                    self.symlink(srcpath,destpath)
        elif os.path.exists(destpath):
            if os.path.isdir(destpath):
                self.merge(src=srcpath,dest=destpath)
            else:
                if self._resolveConflict(src=srcpath, dst=destpath):
                    self.symlink(srcpath,destpath)
                # else keep on trucking.
        else:
            self.symlink(srcpath,destpath)


    def mergeNonDir(self, src, dest, content):
        fdebug('mergeNonDir',locals())
        # src is the stow directory we're merging from
        srcpath = os.path.join( src, content )
        # dest is the target directory that we are dropping
        # symlinks into
        destpath = os.path.join( dest, content )

        if os.path.islink(destpath):
            linkpath = os.path.realpath( destpath )
            if os.path.exists(linkpath):
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
        elif os.path.exists(destpath):
            if self._resolveConflict(src=srcpath, dst=destpath):
                self.symlink(srcpath,destpath)
            # otherwise, we're skipping the conflict
        else:
            self.symlink(srcpath,destpath)

    def unmerge(self,dest,only_dirs=None):
        "Unmerge the package from dest"
        fdebug('unmerge',locals())

        dest = os.path.realpath(dest)

        # We only check these dirs
        if only_dirs is None:
            only_dirs = [dest]
            if self.dirs:
                for directory in self.dirs:
                    only_dirs.append(os.path.join(dest,directory))

        elif dest not in only_dirs:
            # It's not prunable, don't worry about it.
            return False

        if dest == self.package_location:
            return False # It's not empty

        is_empty = True
        for content in os.listdir(dest):
            destpath = os.path.join(dest,content)
            if os.path.islink(destpath):
                linktarget = os.path.realpath(destpath)
                if linktarget.startswith(self.package_location):
                    self.unsymlink(destpath)
                else:
                    is_empty = False
            elif os.path.isdir(destpath):
                is_destpath_empty = self.unmerge(destpath,only_dirs)
                is_empty = is_destpath_empty and is_empty
            else:
                is_empty = False

        if is_empty:
            try:
                os.rmdir(dest)
            except:
                tb = traceback.format_exception( *sys.exc_info() )
                [debug(x) for x in "".join(tb).split('\n')]
                print >> sys.stderr, "Unable to remove directory %s:\n %s" % (
                    dest,tb[-1].rstrip())

        return is_empty

    def install(self,dest,src=None):
        "Install the package"
        fdebug('install',locals())
        _src = src
        if _src is None:
            _src = self.package_location
        preflight = os.path.join(_src,CONTROLDIR,'pre-install');
        if os.access(preflight, os.X_OK):
            os.system(preflight)
        self.merge(dest,src)
        postflight = os.path.join(_src,CONTROLDIR,'post-install');
        if os.access(postflight, os.X_OK):
            os.system(postflight)

    def remove(self,dest,src=None):
        "Remove the package"
        fdebug('remove',locals())
        _src = src
        if _src is None:
            _src = self.package_location
        preflight = os.path.join(_src,CONTROLDIR,'pre-remove');
        if os.access(preflight, os.X_OK):
            os.system(preflight)
        self.unmerge(dest,src)
        postflight = os.path.join(_src,CONTROLDIR,'post-remove');
        if os.access(postflight, os.X_OK):
            os.system(postflight)

# vim: set sw=4 ts=4 expandtab
