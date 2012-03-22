# Welcome to HomeDir

Do you have a home directory? Want to keep it sane, safe, and easy to use on multiple systems?

Then you want HomeDir!

## What is homedir?

It is, in essence, a package manager for your home directory.

It stores *packages* in your `~/.homedir/packages` directory.  These packages can be pulled from my
[examples](https://github.com/docwhat/homedir-examples) or you can set up your own!

This allows you to:

* Version control your home directory files.  Your home directory files represent lots and lots of effort. Why wouldn't you want them archived?
* Share home directory files across multiple hosts.  It's much nicer when all the systems you work on behave the same.

## Requirements

You must have python 2.5 or newer.

## Quick Start

If you've never used HomeDir, then just run this from the command line:

    curl -L -o- https://github.com/docwhat/homedir/raw/master/lib/homedir/setup.py | python

If you don't have curl, then just download (usually right-click and then select "save as...") the file [setup.py](https://github.com/docwhat/homedir/raw/master/lib/homedir/setup.py) and run it with your copy of python.

If you already have `~/bin` in your path, then homedir will "Just Work™".

### Previous HomeDir users

If you've using the pre-2.0 version of HomeDir (hosted on trac.gerf.org) then you should back up your .homedir directory before running the above `setup.py` script.

The main change is that everything in `~/.homedir/files` has been moved to `~/.homedir/packages` and the packages will no longer be automatically updated.

## The Story So Far…

Since about 1999 I've been keeping my home directory config files in
[CVS](http://www.nongnu.org/cvs/). As the number of config files I've
been storing has grown and as the number of different systems I use it
on (my work desktop, my home desktop, my laptop, Gerf, my pda)
increases. As the complexity has grown it has become harder to
maintain.

So, I started looking around for a better solution. I noticed that
[SVN](http://subversion.tigris.org/) is a much better version control
system. I was already familiar with
[stow](http://www.gnu.org/software/stow/stow.html) as well. So I
tinkered around with combining them.

And thus homedir was born!

Since then, I rewrote HomeDir completely in python. This gives me more
control over the help and error messages. I can do better when
conflicts arrive. As well as I can add an elementry package format,
which allows me to solve the problem that uninstalling a stow package
can take forever if you have a lot of directories in your home.

A [friend](http://willnorris.com/) pointed out that the most important
part was the package manager.  The various .dotfiles are interesting
to look at, but most people have their own.  So I moved just the
package manager portion to [github](http://github.com/)

## Similar Ideas

* I have also noticed that [Joey Hess](http://www.kitenet.net/~joey) has
also done something similar and written two articles about it:
  * [CVS homedir, or keeping your life in CVS](http://kitenet.net/~joey/cvshome.html)
  * [Subversion Users: home directory in svn?](http://www.kitenet.net/~joey/svnhome.html)

## Changes since version 1

The original HomeDir, which was hosted on trac.gerf.org, is going to be considered version 1.

### No Configuration File

Version 1 had a configuration file that kept track of where your packages were located.

In this new version packages can be placed anyplace under the directory
`~/.homedir/packages` (except inside another package, of course).

This allows for more flexability for managing packages.

This also means that sync/synccmd is no longer supported.

## Plans/Todo

* Finish moving out the package and dependency checking stuff into a Catalog class.
* Fix cache-tool package in examples.
* Add `homedir-pkg <pkg-name> <file-to-add>...` command to make building a package from existing files easier.
* Get a dedicated freenode #homedir channel: "hello freenode" to mrmist
