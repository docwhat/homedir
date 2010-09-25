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
import urllib2, httplib, tarfile, shutil, errno
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

# Monkey Patch os.makedirs
def makedirs(name, mode=0777):
    """makedirs(path [, mode=0777])

    Super-mkdir; create a leaf directory and all intermediate ones.
    Works like mkdir, except that any intermediate path segment (not
    just the rightmost) will be created if it does not exist.  This is
    recursive.

    Monkey Patched.
    """
    head, tail = os.path.split(name)
    if not tail:
        head, tail = os.path.split(head)
    if head and tail and not os.path.exists(head):
        try:
            makedirs(head, mode)
        except OSError, e:
            # be happy if someone already created the path
            if e.errno != errno.EEXIST:
                raise
        if tail == os.curdir:           # xxx/newdir/. exists if xxx/newdir exists
            return
    try:
        os.mkdir(name, mode)
    except OSError, e:
        # be happy if someone already created the path
        if e.errno != errno.EEXIST:
            raise
os.makedirs = makedirs

class MyTarFile(tarfile.TarFile):

    def extract(self, member, path=""):
        "Modified version of extract that strips out the leading path part."
        self._check('r')
        if not isinstance(member, tarfile.TarInfo):
            member = self.getmember(member)

        if member.islnk():
            fname = member.linkname
        else:
            fname = member.name
        if not fname == 'pax_global_header':
            for i in member.name:
                if fname[0] in (os.path.sep, os.path.altsep):
                    fname = fname[1:]
                    break
                fname = fname[1:]

            if member.islnk():
                member.linkname = fname
            else:
                member.name = fname

            return tarfile.TarFile.extract(self, member, path)
        return True

class Setup:
    "Setup/Install/Configure Homedir."

    def __init__(self, via_web, directory=None):
        if directory is None:
            directory = os.path.expanduser("~/.homedir")
        self.dir = directory
        self.repo_dir = os.path.join(directory, 'repos')
        self.pkg_dir = os.path.join(self.repo_dir, '00required')

        self.via_web = via_web
        self.platform = None

        print "Hey, thanks for trying out HomeDir!"
        print
        print "Let's see what we need to do..."

        # Here's the script...
        self.createDir()
        if via_web:
            self.fetchFiles()
        else:
            self.copyFiles()

        self.installHomedir()

    def createDir(self):
        "Create the directory if it doesn't exist. Offer to clean or purge it if it does."
        if os.path.isdir(self.dir):
            # TODO: Detect new-style install and just choose 'clean'.
            print "Hmmm.... You have a directory called: %s" % self.dir
            print
            print "I can..."
            print "     ...purge the directory, removing the current contents."
            print "     ...clean it out, removing the old homedir core files and replace them with new files."
            print "     ...quit and let you fix things the way you want."
            print

            answer = None
            while answer not in ['p', 'c', 'q']:
                if answer is not None:
                    print
                    print
                    print "Please press one of the following letters: p c q"
                    print
                sys.stdout.write('Should I [p]urge it, [c]lean it up, or just [q]uit? ')
                answer = self.getch().strip().lower()

            print
            if answer == 'p':
                self.purgeDir(self)
            elif answer == 'c':
                self.cleanDir(self)
            else:
                print "Goodbye!"
                sys.exit(0)
        else:
            print "I need to create the directory structure..."
            os.makedirs(self.pkg_dir)
            print "%s is all setup!" % self.dir

    def fetchFiles(self):
        "Retrieve and unpack the files from the web."
        httplib.HTTPConnection.debuglevel = 1
        request = urllib2.Request("http://github.com/docwhat/homedir/tarball/master")
        opener = urllib2.build_opener()
        f = opener.open(request)
        z = MyTarFile.open(fileobj=f, mode='r|*')
        z.extractall(self.pkg_dir)

    def copyFiles(self):
        top = os.path.abspath(__file__)
        for i in range(4):
            top = os.path.dirname(top)

        def ignore(dir, names):
            s = set(['.git', '.svn', 'CVS'])
            for n in names:
                if n.endswith('.pyc'):
                    s.add(n)
            return s

        # This requires the monkey patched os.makedirs().
        shutil.copytree(top, self.pkg_dir, ignore=ignore)

    def installHomedir(self):
        "Install/upgrade homedir's package"
        raise "TODO: Need to python execute homedir."

    def getch(self):
        "Returns a single character"
        if self.platform is None:
            try:
                # Window's python?
                import msvcrt
                self.platform = 'windows'
            except ImportError:
                # Fallback...
                self.platform = 'unix'

        if self.platform == 'windows':
            import msvcrt
            return msvcrt.getch()
        else:
            import sys, tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch


if __name__ == "__main__":
    if sys.version_info < (2,5):
        print >> sys.stderr, "This program requires python 2.5.\nYou're running python %s" % sys.version
        sys.exit(1)
    Setup(via_web=("<stdin>" == __file__))

# vim: set sw=4 ts=4 expandtab
