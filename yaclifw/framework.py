#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2014 University of Dundee & Open Microscopy Environment
# All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
Framework copied from openmicroscopy/snoopycrimecop for
registering commands. This is also used by the omego and
scc PyPI packages.

See the documentation on each Command subclass for specifics.

Environment variables:
    YACLIFW_DEBUG_LEVEL     default: logging.INFO

"""

import os
import sys
import logging

FRAMEWORK_NAME = "yaclifw"
DEBUG_LEVEL = logging.INFO


argparse_loaded = True
try:
    import argparse
except ImportError:
    print >> sys.stderr, \
        "Module argparse missing. Install via 'pip install argparse'"
    argparse_loaded = False


#
# Exceptions
#

class Stop(Exception):
    """
    Exception which specifies that the current execution has finished.
    This is useful when an appropriate user error message has been
    printed and it's not necessary to print a full stacktrace.
    """

    def __init__(self, rc, *args, **kwargs):
        self.rc = rc
        super(Stop, self).__init__(*args, **kwargs)


#
# What follows are the commands which are available from the command-line.
# Alphabetically listed please.
#

class Command(object):
    """
    Base type. At the moment just a marker class which
    signifies that a subclass is a CLI command. Subclasses
    should register themselves with the parser during
    instantiation. Note: Command.__call__ implementations
    are responsible for calling cleanup()
    """

    NAME = "abstract"

    def __init__(self, sub_parsers, set_defaults=True):
        self.log = logging.getLogger("%s.%s" % (FRAMEWORK_NAME, self.NAME))
        self.log_level = DEBUG_LEVEL

        help = self.__doc__
        if help:
            help = help.lstrip()
        self.parser = sub_parsers.add_parser(self.NAME,
                                             help=help, description=help)
        if set_defaults:
            self.parser.set_defaults(func=self.__call__)

        self.parser.add_argument(
            "-v", "--verbose", action="count", default=0,
            help="Increase the logging level by multiples of 10")
        self.parser.add_argument(
            "-q", "--quiet", action="count", default=0,
            help="Decrease the logging level by multiples of 10")

    def __call__(self, args):
        self.configure_logging(args)
        self.cwd = os.path.abspath(os.getcwd())

    def configure_logging(self, args):
        self.log_level += args.quiet * 10
        self.log_level -= args.verbose * 10

        format = "%(asctime)s [%(name)12.12s] %(levelname)-5.5s %(message)s"
        logging.basicConfig(level=self.log_level, format=format)
        logging.getLogger('github').setLevel(logging.INFO)

        self.log = logging.getLogger('%s.%s' % (FRAMEWORK_NAME, self.NAME))
        self.dbg = self.log.debug


def parsers():

    class HelpFormatter(argparse.RawTextHelpFormatter):
        """
        argparse.HelpFormatter subclass which cleans up our usage,
        preventing very long lines in subcommands.

        Borrowed from omero/cli.py
        Defined inside of parsers() in case argparse is not installed.
        """

        def __init__(self, prog, indent_increment=2, max_help_position=40,
                     width=None):

            argparse.RawTextHelpFormatter.__init__(
                self, prog, indent_increment, max_help_position, width)

            self._action_max_length = 20

        def _split_lines(self, text, width):
            return [text.splitlines()[0]]

        class _Section(argparse.RawTextHelpFormatter._Section):

            def __init__(self, formatter, parent, heading=None):
                argparse.RawTextHelpFormatter._Section.__init__(
                    self, formatter, parent, heading)

    yaclifw_parser = argparse.ArgumentParser(
        description='omego - installation and administration tool',
        formatter_class=HelpFormatter)
    sub_parsers = yaclifw_parser.add_subparsers(title="Subcommands")

    return yaclifw_parser, sub_parsers


def main(fw_name, args=None, items=None):
    """
    Reusable entry point. Arguments are parsed
    via the argparse-subcommands configured via
    each Command class found in globals(). Stop
    exceptions are propagated to callers.

    The name of the framework will be used in logging
    and similar.
    """

    global DEBUG_LEVEL
    global FRAMEWORK_NAME

    debug_name = "%s_DEBUG_LEVEL" % fw_name.upper()
    if debug_name in os.environ:
        try:
            DEBUG_LEVEL = int(os.environ.get(debug_name))
        except:
            DEBUG_LEVEL = 10  # Assume poorly formatted means "debug"
    FRAMEWORK_NAME = fw_name

    if not argparse_loaded:
        raise Stop(2, "Missing required module")

    if args is None:
        args = sys.argv[1:]

    if items is None:
        items = globals().items()

    yaclifw_parser, sub_parsers = parsers()

    for name, MyCommand in sorted(items):
        if not isinstance(MyCommand, type):
            continue
        if not issubclass(MyCommand, Command):
            continue
        if MyCommand.NAME == "abstract":
            continue
        MyCommand(sub_parsers)

    ns = yaclifw_parser.parse_args(args)
    ns.func(ns)
    if hasattr(ns, 'callback'):
        if callable(ns.callback):
            ns.callback()
        else:
            raise Stop(3, "Callback not callable")
