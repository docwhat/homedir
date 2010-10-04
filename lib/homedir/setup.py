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
import urllib2, httplib, tarfile, shutil, errno, subprocess
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

DIRVERSION=2
class UnknownDirVersion(StandardError):
    pass

def getch():
    "Returns a single character"
    if getch.platform is None:
        try:
            # Window's python?
            import msvcrt
            getch.platform = 'windows'
        except ImportError:
            # Fallback...
            try:
                import tty, termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                getch.platform = 'unix'
            except termios.error:
                getch.platform = 'dumb'

    if getch.platform == 'windows':
        import msvcrt
        return msvcrt.getch()
    elif getch.platform == 'unix':
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    else:
        return sys.stdin.read(1).strip().lower()
getch.platform = None

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

def copytree(src, dst):
    "A copy tree that doesn't copy .git, .svn, etc."
    names = os.listdir(src)
    makedirs(dst)
    errors = []
    for name in names:
        if name in set(['.git', '.svn', 'CVS']) or name.endswith('.pyc'):
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname)
            else:
                shutil.copy2(srcname, dstname)
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        except StandardError, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error, errors

def msg(s):
    print " * %s" % s

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

        self.via_web = via_web

        print "Setting up HomeDir!"
        print

        # Here's the script...
        self.createDir()
        self.getFiles()
        self.installFiles()
        self.fixHashBang()
        self.cleanup()
        msg("Done!")

        print
        bindir = os.path.expanduser("~/bin")
        if bindir in os.getenv('PATH', '').split(os.pathsep):
            print "You're all setup and can now run the command 'homedir'."
        else:
            print "HomeDir is installed, however $HOME/bin is not in your PATH."
            print "You can either manually run HomeDir from your directory or"
            print "you can modify your shell startup scripts to include ~/bin"

    def detectDirVersion(self):
        "Detects the version of the .homedir directory"
        """
        Versions:
        0 - No version.
        1 - Original Homedir as hosted on http://trac.gerf.org/homedir
        2 - New Homedir.
        """
        pj = os.path.join
        if not os.path.isdir(self.dir):
            return 0
        if os.path.isdir(pj(self.dir, 'files')) and \
           os.path.isdir(pj(self.dir, 'cache')):
            return 1
        if os.path.isfile(pj(self.dir, '.version')):
            f = file(pj(self.dir, '.version'))
            try:
                version = f.readline().strip()
            finally:
                f.close()
            return int(version)

        print UnknownDirVersion("I got no clue what your .homedir is.")
        raise UnknownDirVersion("I got no clue what your .homedir is.")

    def createDir(self):
        "Create the directory if it doesn't exist. Offer to clean or purge it if it does."
        try:
            version = self.detectDirVersion()
        except UnknownDirVersion:
            print "You already have a directory called %s" % self.dir
            print "but I don't know what it is."
            print
            print "I can..."
            print "     ...purge the directory, removing the current contents."
            print "     or"
            print "     ...quit and let you fix things the way you want."
            print

            answer = None
            while answer not in ['p', 'q']:
                if answer is not None:
                    print
                    print
                    print "Please press one of the following letters: p q"
                    print
                sys.stdout.write('Should I [p]urge it, or just [q]uit? ')
                answer = getch().strip().lower()

            print
            if answer == 'p':
                self.purgeDir(self)
                version = 0
            else:
                print "Goodbye!"
                sys.exit(0)

        msg("Updating directory...")
        while version < DIRVERSION:
            getattr(self, "updateVersion%d" % version)()
            version += 1
        f = file(os.path.join(self.dir, '.version'), 'w')
        try:
            f.write("%d%s" % (DIRVERSION, os.linesep))
        finally:
            f.close()

    def purgeDir(self):
        "Deletes the current ~/.homedir directory."
        shutil.rmtree(os.path.join(self.dir), ignore_errors=True)

    def getFiles(self):
        "Copy files instead of getting them from the web."
        shutil.rmtree(os.path.join(self.dir, 'tmp'), ignore_errors=True)
        dst=os.path.join(self.dir, 'tmp')

        if self.via_web:
            msg("Fetching latest version of homedir...")
            httplib.HTTPConnection.debuglevel = 1
            request = urllib2.Request("http://github.com/docwhat/homedir/tarball/master")
            opener = urllib2.build_opener()
            f = opener.open(request)
            z = MyTarFile.open(fileobj=f, mode='r|*')
            z.extractall(dst)
        else:
            msg("Copying homedir from files...")
            src = os.path.abspath(__file__)
            for i in range(3):
                src = os.path.dirname(src)
            copytree(src, dst)

    def installFiles(self):
        "This copies the files into their proper location in .homedir and symlinks them into $HOME"
        msg("Installing files...")
        pj = os.path.join
        for e in ('bin', 'lib'):
            src = pj(self.dir, 'tmp', e)
            dst = pj(self.dir, e)
            shutil.rmtree(dst, ignore_errors=True)
            copytree(src, dst)

        bindir = os.path.expanduser("~/bin")
        makedirs(bindir)
        for e in os.listdir(pj(self.dir, 'bin')):
            src = pj(os.path.pardir, '.homedir', 'bin', e)
            dst = pj(bindir, e)
            if os.path.islink(dst):
                os.unlink(dst)
            os.symlink(src, dst)

    def fixHashBang(self):
        "Go through all the python scripts and fix the hash-bangs."
        msg("Fixing hashbangs...")
        bindir = os.path.join(self.dir, 'bin')
        for entry in os.listdir(bindir):
            p = os.path.join(bindir, entry)
            if os.path.isfile(p):
                fd = file(p, 'r')
                hashbang = fd.readline()
                if hashbang.startswith('#!') and 'python' in hashbang:
                    data = "#!%s -utWall\n" % (sys.executable) + fd.read()
                    fd.close()
                    fd = file(p, 'w')
                    fd.write(data)
                fd.close()

    def cleanup(self):
        pj = os.path.join
        shutil.rmtree(pj(self.dir, 'tmp'), ignore_errors=True)

    def updateVersion0(self):
        "Creates a base .homedir"
        makedirs(self.dir)

    def updateVersion1(self):
        "Updates from old style homedir to the new layout."
        pj = os.path.join
        makedirs(pj(self.dir, 'bin'))
        makedirs(pj(self.dir, 'lib'))
        makedirs(pj(self.dir, 'packages'))
        if os.path.isfile(pj(self.dir, 'config')):
            os.rename(pj(self.dir, 'config'), pj(self.dir, 'config-is-nolonger-used'))

        # We don't need these.
        shutil.rmtree(pj(self.dir, 'files', 'unittest'), ignore_errors=True)
        if os.path.isfile(pj(self.dir, 'files', 'setup')):
            os.unlink(pj(self.dir, 'files', 'setup'))

        if os.path.isdir(pj(self.dir, 'files')):
            os.rename(pj(self.dir, 'files'), pj(self.dir, 'packages'))

        old_homedir = pj(self.dir, 'packages', 'packages', '00homedir')
        if os.path.isdir(old_homedir):
            shutil.rmtree(old_homedir, ignore_errors=True)

        #shutil.rmtree(pj(self.dir, 'cache'), ignore_errors=True)


if __name__ == "__main__":
    if sys.version_info < (2,5):
        print >> sys.stderr, "This program requires python 2.5.\nYou're running python %s" % sys.version
        sys.exit(1)
    Setup(via_web=("<stdin>" == __file__))

# vim: set sw=4 ts=4 expandtab
