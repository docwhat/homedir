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
import urllib2, httplib, zipfile, shutil
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class MyZipFile(zipfile.ZipFile):

    def extract(self, member, path=None, pwd=None):
        "Modified version of extract that strips out the leading path part."
        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)

        fname = member.filename
        for i in member.filename:
            if fname[0] in (os.path.sep, os.path.altsep):
                break
            fname = fname[1:]

        member.filename = fname

        return zipfile.ZipFile.extract(self, member, path, pwd)

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
            os.mkdir(self.dir)
            os.mkdir(self.repo_dir)
            os.mkdir(self.pkg_dir)
            print "%s is all setup!" % self.dir

    def fetchFiles(self):
        "Retrieve and unzip the files from the web."
        httplib.HTTPConnection.debuglevel = 1
        request = urllib2.Request("http://github.com/docwhat/homedir/zipball/master")
        opener = urllib2.build_opener()
        # TODO: Figure out how to stream this instead of doing it in memory.
        f = opener.open(request)
        sio = StringIO()
        sio.write(f.read())
        sio.seek(0)
        z = MyZipFile(sio)
        z.extractall(self.dir)

    def installHomedir(self):
        "Install/upgrade homedir's package"
        raise "TODO: Need to python executa homedir."

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
    if sys.version_info < (2,6):
        print >> sys.stderr, "This program requires python 2.6.\nYou're running python %s" % sys.version
        sys.exit(1)
    Setup(via_web=("<stdin>" == __file__))

# vim: set sw=4 ts=4 expandtab
