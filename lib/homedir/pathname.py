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

import os, shutil

class Pathname:
    """
    A class to wrap a filesystem path object. This makes working with lots of paths easier.

    Based on 
    """
    def __init__(self, *path):
        path = [unicode(x) for x in path]
        self._path = os.path.normcase(unicode(os.path.join(*path)).rstrip(os.path.sep).rstrip(os.path.altsep))

    def __str__(self):
        return self._path

    def __repr__(self):
        return u'<%s id="%s" path="%s">' % (self.__class__.__name__, id(self), self._path)

    def __add__(self, other):
        return Pathname(os.path.join(self._path, unicode(other)))

    def __eq__(self, other):
        return self._path == os.path.normcase(unicode(other))

    def basename(self):
        return Pathname(os.path.basename(self._path))

    def dirname(self):
        return Pathname(os.path.dirname(self._path))

    def realpath(self):
        return Pathname(os.path.realpath(self._path))

    def normalize(self):
        "expands variables, deals with ~/, fixes case, and removes double slashes"
        return Pathname(
            os.path.expanduser(
                os.path.expandvars(
                    os.path.normpath(
                        os.path.normcase(
                            self._path
                            )))))

    def exists(self):
        return os.path.exists(self._path)

    def isfile(self):
        return os.path.isfile(self._path)

    def isdir(self):
        return os.path.isdir(self._path)

    def islink(self):
        return os.path.islink(self._path)

    def isabs(self):
        return os.path.isabs(self._path)

    def access(self, *args):
        return os.access(self._path, *args)

    def listdir(self):
        return tuple([Pathname(x) for x in os.listdir(self._path)])

    def readlink(self):
        return Pathname(os.readlink(self._path))

    def mkdir(self):
        return os.mkdir(self._path)

    def rmdir(self):
        return os.rmdir(self._path)

    def rm_rf(self, ignore_errors=False):
        return shutil.rmtree(self._path, ignore_errors)

    def unlink(self):
        return os.unlink(self._path)

    def open(self, *args, **kwargs):
        return file(self._path, *args, **kwargs)

    def symlink(self, dest):
        "Symlink the current Pathname to the dest."
        return os.symlink(self._path, unicode(dest))

    def split(self):
        head, tail = os.path.split(self._path)
        return (Pathname(head), Pathname(tail))

    def rename(self, dest):
        return os.rename(self._path, unicode(dest))

    def relative_path_from(self, base):
        """Returns the a path to self, relative to base.

        Both self and base must be either relative or absolute; you cannot mix.

        Note: This method doesn't touch the filesystem. You must resolve symlinks, etc. your self first.
        """
        "Algorithm taken from pathname.rb from Ruby 1.9.2"
        base = Pathname(base)

        if self.isabs() and base.isabs():
            is_rel = False
        elif not self.isabs() and not base.isabs():
            is_rel = True
        else:
            raise ValueError("self and base must both be relative or absolute!")

        a_prefix = self._path
        a_names = []

        b_prefix = base._path
        b_names = []

        a_prefix, basename = os.path.split(a_prefix)
        while a_prefix != '' and basename != '':
            if basename != os.path.curdir:
                a_names.insert(0, basename)
            a_prefix, basename = os.path.split(a_prefix)

        b_prefix, basename = os.path.split(b_prefix)
        while b_prefix != '' and basename != '':
            if basename != os.path.curdir:
                b_names.insert(0, basename)
            b_prefix, basename = os.path.split(b_prefix)

        if a_prefix != b_prefix:
            raise "different prefix: %r and %r" % (a_prefix, b_prefix)

        while a_names and b_names and a_names[0] == b_names[0]:
            a_names.pop(0)
            b_names.pop(0)

        if os.path.pardir in b_names:
            raise ValueError, "base includes .. in path: %r" % base

        b_names = [os.path.pardir for x in b_names]
        relpath = b_names + a_names

        if relpath:
            return Pathname(*relpath)
        else:
            return Pathname(os.path.curdir)

    def is_subdir_of(self, other):
        "Returns true if other is a subdirectory of self."
        other = Pathname(other)

        other_parts = []
        other_prefix = other._path
        self_parts  = []
        self_prefix = self._path

        other_prefix, basename = os.path.split(other_prefix)
        while other_prefix != '' and basename != '':
            if basename != os.path.curdir:
                other_parts.insert(0, basename)
            other_prefix, basename = os.path.split(other_prefix)

        self_prefix, basename = os.path.split(self_prefix)
        while self_prefix != '' and basename != '':
            if basename != os.path.curdir:
                self_parts.insert(0, basename)
            self_prefix, basename = os.path.split(self_prefix)

        if other_prefix != self_prefix:
            raise "different prefix: %r and %r" % (self_prefix, other_prefix)

        other_path = os.path.sep.join(other_parts) + os.path.sep
        self_path = os.path.sep.join(self_parts)

        return self_path.startswith(other_path)

if __name__ == "__main__":
    import unittest, re, tempfile

    class PathnameTestCase(unittest.TestCase):

        def testInit(self):
            p1 = Pathname('tmp', 'fish', 'blah')
            p2 = Pathname(p1)
            p3 = Pathname(*p2.split())
            self.assertEqual(p1, p2)
            self.assertEqual(p1, p3)

        def testCompare(self):
            p1 = Pathname('tmp', 'fish', 'blah')
            p2 = Pathname(os.path.join('tmp', 'fish', 'blah'))
            self.assertEqual(p1, p2)

            p3 = Pathname('tmp', 'fish', 'blah', '')
            self.assertEqual(p1, p3)

        def testStr(self):
            expected = os.path.join('tmp','fish','blah')
            got = unicode(Pathname(expected))
            self.assertEquals(got, expected)

        def testRepr(self):
            regex = re.compile('^<([A-Za-z]+)\s+id="([^"]+)"\s+path="([^"]+)">$')
            expected_path = os.path.join('tmp','fish','blah')
            p1 = Pathname(expected_path)
            self.assertTrue(p1 is not None)

            match = regex.search(repr(p1))
            self.assertEqual(match.group(1), 'Pathname')
            p1_id = match.group(2)
            self.assertEqual(match.group(3), expected_path)

            p2 = Pathname(expected_path)
            match = regex.search(repr(p2))
            self.assertEqual(match.group(1), 'Pathname')
            p2_id = match.group(2)
            self.assertEqual(match.group(3), expected_path)

            self.assertNotEqual(p1_id, p2_id)

        def testBasename(self):
            p = Pathname(os.path.join('tmp','fish','blah'))
            expected = 'blah'
            self.assertEqual(unicode(p.basename()), expected)

        def testDirname(self):
            p = Pathname(os.path.join('tmp','fish','blah'))
            expected = os.path.join('tmp','fish')
            self.assertEqual(unicode(p.dirname()), expected)

        def testAdd(self):
            p = Pathname(os.path.join('tmp','fish')) + 'blah'
            expected = os.path.join('tmp','fish','blah')
            self.assertEqual(unicode(p), expected)

            p = Pathname(os.path.join('tmp','fish')) + Pathname('blah')
            self.assertEqual(unicode(p), expected)

            p = Pathname('tmp') + 'fish' + 'blah'
            self.assertEqual(unicode(p), expected)

        def testIn(self):
            l = ('tmp', 'mouse', 'cat')
            for i in l:
                self.assertTrue(Pathname(i) in l)

        def testRelativePathFrom(self):
            s = os.path.sep
            pd = os.path.pardir
            cd = os.path.curdir
            p1a = Pathname(s, 'a','b','q',cd,'r')
            p2a = Pathname(s, 'a','b',cd,'c','d','e','f')
            p1r = Pathname('a','b','q','r',cd)
            p2r = Pathname('a',cd,'b','c','d','e','f')

            expected21 = Pathname(pd, pd, 'c','d','e','f')
            expected12 = Pathname(pd, pd, pd, pd, 'q', 'r')

            self.assertRaises(ValueError, p2a.relative_path_from, p1r)
            self.assertRaises(ValueError, p2r.relative_path_from, p1a)

            self.assertEqual(p2a.relative_path_from(p1a),
                             expected21)
            self.assertEqual(p1a.relative_path_from(p2a),
                             expected12)

            self.assertEqual(p2r.relative_path_from(p1r),
                             expected21)
            self.assertEqual(p1r.relative_path_from(p2r),
                             expected12)

        def testIsSubdirOf(self):
            s = os.path.sep
            cd = os.path.curdir
            p1a = Pathname(s,'a','b')
            p2a = Pathname(s,'a',cd,'b','c','d')

            p1r = Pathname('a',cd,'b')
            p2r = Pathname('a','b','c','d')

            self.assertFalse(p1a.is_subdir_of(p2a))
            self.assertTrue (p2a.is_subdir_of(p1a))

            self.assertFalse(p1r.is_subdir_of(p2r))
            self.assertTrue (p2r.is_subdir_of(p1r))

        def testIsSubdirOf2(self):
            top = Pathname(os.path.sep, 'Users','docwhat','.homedir','packages','homedir-examples','emacs-base')
            sub = Pathname(os.path.sep, 'Users','docwhat','.homedir','packages','homedir-examples','emacs-base','.emacs')

            self.assertTrue (sub.is_subdir_of(top))
            self.assertFalse(top.is_subdir_of(sub))

        def testIs(self):
            d = Pathname(tempfile.mkdtemp())
            try:
                # Name them.
                dd  = d + 'dir'
                ddl = d + 'dir_link'
                df  = d + 'file'
                dfl = d + 'file_link'
                dbl = d + 'broken_link'

                # Make them.
                dd.mkdir()
                dd.symlink(ddl)

                f = df.open('w')
                f.write("text\n")
                f.close()
                df.symlink(dfl)

                (d + 'not-a-real-location').symlink(dbl)

                # Test them.
                self.assertTrue (dd.isdir())
                self.assertFalse(dd.isfile())
                self.assertFalse(dd.islink())
                self.assertTrue (dd.exists())

                self.assertTrue (ddl.isdir())
                self.assertFalse(ddl.isfile())
                self.assertTrue (ddl.islink())
                self.assertTrue (dd.exists())

                self.assertFalse(df.isdir())
                self.assertTrue (df.isfile())
                self.assertFalse(df.islink())
                self.assertTrue (dd.exists())

                self.assertFalse(dfl.isdir())
                self.assertTrue (dfl.isfile())
                self.assertTrue (dfl.islink())
                self.assertTrue (dd.exists())

                self.assertFalse(dbl.isdir())
                self.assertFalse(dbl.isfile())
                self.assertTrue (dbl.islink())
                self.assertTrue (dd.exists())

            finally:
                d.rm_rf()

    unittest.main()
# === Core methods
#
# These methods are effectively manipulating a String, because that's
# all a path is.  Except for #mountpoint?, #children, #each_child,
# #realdirpath and #realpath, they don't access the filesystem.
#
# - +
# - #join
# - #parent
# - #root?
# - #absolute?
# - #relative?
# - #relative_path_from
# - #each_filename
# - #cleanpath
# - #realpath
# - #realdirpath
# - #children
# - #each_child
# - #mountpoint?
#
# === File status predicate methods
#
# These methods are a facade for FileTest:
# - #blockdev?
# - #chardev?
# - #directory?
# - #executable?
# - #executable_real?
# - #exist?
# - #file?
# - #grpowned?
# - #owned?
# - #pipe?
# - #readable?
# - #world_readable?
# - #readable_real?
# - #setgid?
# - #setuid?
# - #size
# - #size?
# - #socket?
# - #sticky?
# - #symlink?
# - #writable?
# - #world_writable?
# - #writable_real?
# - #zero?
#
# === File property and manipulation methods
#
# These methods are a facade for File:
# - #atime
# - #ctime
# - #mtime
# - #chmod(mode)
# - #lchmod(mode)
# - #chown(owner, group)
# - #lchown(owner, group)
# - #fnmatch(pattern, *args)
# - #fnmatch?(pattern, *args)
# - #ftype
# - #make_link(old)
# - #open(*args, &block)
# - #readlink
# - #rename(to)
# - #stat
# - #lstat
# - #make_symlink(old)
# - #truncate(length)
# - #utime(atime, mtime)
# - #basename(*args)
# - #dirname
# - #extname
# - #expand_path(*args)
# - #split
    

        
