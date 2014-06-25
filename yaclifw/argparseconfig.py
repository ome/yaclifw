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
A combination of command-line argument parsing using argparse and
configuration file options using ConfigParser
"""

import argparse
import ConfigParser


def set_action_default_from_config(action, config_dict):
    """
    If config_dict contains a matching key matching action.dest then use this
    to set the default value of the argparse action object
    """
    if config_dict:
        try:
            assert action.dest
            default = config_dict[action.dest]
            if action.type:
                default = action.type(default)
            print 'Default %s: %s -> %s' % (
                action.dest, action.default, default)
            action.default = default
        except KeyError:
            pass


def boolconv(s):
    """
    Converts a string to a bool
    """
    if s.lower() in ('0', 'false'):
        return False
    if s.lower() in ('1', 'true'):
        return True
    raise Exception('Invalid boolean string: %s' % s)


class ArgumentGroupParser(object):
    """
    Overrides the add_argument method of the object returned by
    ArgumentParser.add_argument_group()
    """

    def __init__(self, group, config_dict):
        self.group = group
        self.config_dict = config_dict

    def add_argument(self, *args, **kwargs):
        """
        Overrides add_argument so that the string values from a configuration
        file can be converted to the required type if specified.
        """
        has_default = 'default' in kwargs
        print 'ArgumentGroupParser.add_argument', args, kwargs, has_default
        action = self.group.add_argument(*args, **kwargs)
        if kwargs.get('action') == 'count':
            setattr(action, 'type', int)
        if kwargs.get('action') in ('store_true', 'store_false'):
            setattr(action, 'type', boolconv)
        set_action_default_from_config(action, self.config_dict)
        return action

    def __getattr__(self, name):
        return getattr(self.group, name)


class ArgparseConfigParser(argparse.ArgumentParser):
    """
    An ArgumentParser that uses ConfigParser values as defaults, inspired by
    http://blog.vwelch.com/2011/04/combining-configparser-and-argparse.html

    Instead of using ArgumentParser.set_defaults() this overrides
    ArgumentParser.add_argument so that the `type` argument can be used to
    convert strings from the ConfigParser into the specified type

    Optional keyword arguments:
      Only one of config_dict or config_parser can be provided
      config_dict, dict: A dictionary of arguments and default values, for
        example dict(ConfigParser.items())
      config_parser, ConfigParser: A ConfigParser object, if specified then
        config_section should also be given
      config_section, str: The ConfigParser section name, if not specified
        then no config values will be used for this parser
      ignore_missing, bool: If True (default) missing configuration
        sections will be ignored. If configuration files are optional this
        must be True.


    Overridden methods

    add_argument()
      Overrides add_argument so that the string values from a configuration
      file can be converted to the required type if necessary. Also checks
      for a limited set of known action types to infer the required type
      (count:int, store_true:bool, store_false:bool)

    add_argument_group(..., config_dict=dict, config_section=str)
      Takes an optional set of config file values, one of the following can be
      specified:
        config_dict, dict: A dictionary of arguments and default values
        config_section, str: The ConfigParser section name, a config_parser
          must have been provided when constructing the ArgparseConfigParser

    add_subparsers()
      Returns a modified subparsers object that includes a link to the parent
      config values. This object includes a method addparser().

      addparser()
        Takes the same optional config arguments as ArgparseConfigParser,
        except that config_parser from the parent parser will be automatically
        set if not otherwise provided, so just config_section can be
        specified.


    Additional methods

    add_and_parse_config_files(*optionargs,
        args=None, config_section=None, add_help=True, add_to_self=False)
      Looks for config-files, and attempts to parse them. If multiple
      config-file arguments are passed they will be merged with values from
      later files overridding earlier ones.

      The configurations will be added to this object. If add_to_self is True
      then the argument parser will be added to this object, otherwise they
      will be added to a separate parser.

      Note this will call parse_known_args() to find any config files in the
      command line arguments. This means if help was requested the parser will
      exit before all other arguments have been added. To prevent this pass
      add_help=False to ArgparseConfigParser, and add it after the initial
      parse to find the config files has been completed.

      optionargs: short and/or long option names for indicating config file
        arguments
      args: Optional, array of arguments to be parsed
      config_section: The name of the section in the config-file to use
      add_help: Whether to add a help argument
      return: (parsed_args, remaining_args, config)
        parsed_args: A Namespace object containing the parsed arguments
        remaining_args: Array of args which weren't parsed
        config: The ConfigParser object with all config files combined
      e.g. add_and_parse_config_files(
             '-c', '--conffile', ..., config_section='section')

    set_config(config_parser, config_section=None)
      Sets or changes the config_parser, see above


    Examples:

    config = ConfigParser.SafeConfigParser()
    # config.cfg must contain sections 'main', 'subparser' and 'subgroup'
    config.read('config.cfg')
    config_main = config.items('main')
    config_subparser = config.items('subparser')
    config_group = config.items('subgroup')

    parser = ArgparseConfigParser(config_dict=dict(config_main))
    group = parser.add_argument_group('title', config_dict=dict(config_group))

    parser = ArgparseConfigParser(config_parser=config, config_section='main')
    subparsers = parser.add_subparsers(title='Subparsers')
    subparser = subparsers.add_parser(
        'subparser', help='Subparser help', config_section='subparser')
    group = subparser.add_argument_group('title', config_section='subgroup')

    argv = '-c f1.cfg -c f2.cfg -a 1 -b 1'.split()
    parser = ArgparseConfigParser(add_help=False)
    parsed, remaining, config = parser.add_and_parse_config_files(
        '-c', '--conffile', args=argv, config_section='section', add_help=True)
    # c1.cfg and c2.cfg will be read and the required section used to set the
    # defaults for subsequent add_argument() calls
    parser.add_argument('-a', help='Help for a')
    args = parser.parse_args(remaining)
    """

    def __init__(self, *args, **kwargs):
        self.config_dict = kwargs.pop('config_dict', None)
        self.config_parser = kwargs.pop('config_parser', None)
        config_section = kwargs.pop('config_section', None)
        self.ignore_missing = bool(kwargs.pop('ignore_missing', True))

        if self.config_dict and self.config_parser:
            raise Exception('Invalid combination of arguments')
        if self.config_parser:
            self.config_dict = self.get_config_section(config_section)

        super(ArgparseConfigParser, self).__init__(*args, **kwargs)
        self.subparsers = None

    def add_and_parse_config_files(self, *optionargs, **kwargs):
        # Must disable help, otherwise parse_args will exit prematurely before
        # the subparsers have been added. Unfortunately this means the config
        # files will always be read even if help is specified

        args = kwargs.pop('args', None)
        config_section = kwargs.pop('config_section', None)
        add_help = kwargs.pop('add_help', True)
        add_to_self = kwargs.pop('add_to_self', False)

        if add_to_self:
            cfgparser = self
        else:
            cfgparser = ArgparseConfigParser(add_help=False)
        cfgparser.add_argument(
            *optionargs, action='append', default=[],
            help='Configuration file (can be repeated)', metavar='FILE.cfg')

        parsed_args, remaining_args = cfgparser.parse_known_args(args)
        config = ConfigParser.SafeConfigParser()
        # TODO: Read defaults in from a file
        # config.readfp(open('defaults.cfg'))
        if parsed_args.conffile:
            files_read = config.read(parsed_args.conffile)
        else:
            files_read = []
        unread = set(parsed_args.conffile) - set(files_read)
        if unread:
            raise Exception(
                'Failed to read configuration file(s): %s' % ' '.join(unread))

        if add_help:
            cfgparser.add_argument(
                '-h', '--help', action='help', default=argparse.SUPPRESS,
                help='show this help message and exit')

        self.set_config(config, config_section)
        return parsed_args, remaining_args, config, cfgparser

    def add_argument(self, *args, **kwargs):
        has_default = 'default' in kwargs
        print 'ArgparseConfigParser.add_argument', args, kwargs, has_default
        action = super(ArgparseConfigParser, self).add_argument(
            *args, **kwargs)
        if kwargs.get('action') == 'count':
            setattr(action, 'type', int)
        if kwargs.get('action') in ('store_true', 'store_false'):
            setattr(action, 'type', boolconv)
        print action.type
        set_action_default_from_config(action, self.config_dict)
        return action

    def add_argument_group(self, *args, **kwargs):
        print 'ArgparseConfigParser.add_argument_group', args, kwargs
        group_config_section = kwargs.pop('config_section', None)
        group_config_dict = kwargs.pop('config_dict', None)

        if group_config_section and group_config_dict is not None:
            raise Exception('Invalid combination of arguments')

        if group_config_section is not None:
            if not self.config_parser:
                raise Exception('No ConfigParser was provided')
            group_config_dict = self.get_config_section(group_config_section)
        elif group_config_dict is None:
            group_config_dict = self.config_dict
        # Allow {} to indicate no config values

        group = super(ArgparseConfigParser, self).add_argument_group(
            *args, **kwargs)
        return ArgumentGroupParser(group, group_config_dict)

    def add_subparsers(self, *args, **kwargs):
        class SubParsers:
            def __init__(self, parent):
                self.parent = parent

            def add_parser(self, *args, **kwargs):
                kwargs.setdefault('config_parser', self.parent.config_parser)
                return self.parent.subparsers.add_parser(*args, **kwargs)

        self.subparsers = super(ArgparseConfigParser, self).add_subparsers(
            *args, **kwargs)
        return SubParsers(self)

    def set_config(self, config_parser, config_section=None):
        self.config_parser = config_parser
        self.config_dict = self.get_config_section(config_section)

    def get_config_section(self, section):
        if section is None:
            return {}
            # raise Exception('No ConfigParser section name provided')
        try:
            return dict(self.config_parser.items(section))
        except ConfigParser.NoSectionError:
            if self.ignore_missing:
                return {}
            raise
