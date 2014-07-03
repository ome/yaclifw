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

import pytest

import argparse
from ConfigParser import SafeConfigParser, NoSectionError
from yaclifw import argparseconfig


class TestArgparseConfigParser(object):

    def setup_method(self, method):
        cp = SafeConfigParser()

        cp.add_section('main')
        cp.set('main', 'int', '1')

        cp.add_section('subparser1')
        cp.set('subparser1', 'string', 'a string')

        cp.add_section('subgroup1')
        cp.set('subgroup1', 'float', '2.3')

        self.cp = cp

    def assert_args_equal(self, refdict, args):
        """
        Asserts that the list of public attributes of an object and the values
        of those attributes are equal to refdict
        """
        assert refdict == args.__dict__

    def assert_args_contains(self, refdict, obj):
        """
        Asserts that the list of public attributes of an object and the values
        of those attributes includes those in refdict
        """
        for k, v in refdict.iteritems():
            assert hasattr(obj, k)
            assert getattr(obj, k) == v

    @pytest.mark.parametrize('mode', ['noargs', 'args'])
    @pytest.mark.parametrize('add_to_self', [True, False])
    def test_add_and_parse_config_files(self, tmpdir, mode, add_to_self):
        cfg1txt = [
            '[main]',
            'a = 1',
            '[subgroup]',
            'b = 2',
        ]
        cfg2txt = [
            '[subgroup]',
            'b = 3'
        ]

        cfg1 = tmpdir.join('f1.cfg')
        cfg1.write('\n'.join(cfg1txt))
        cfg2 = tmpdir.join('f2.cfg')
        cfg2.write('\n'.join(cfg2txt))

        argv1 = ['-c', str(cfg1), '--conffile', str(cfg2)]
        if mode == 'noargs':
            argv2 = []
            expected2 = {'a': 1, 'b': None}
        else:
            argv2 = ['-a', '10', '-b', '20']
            expected2 = {'a': 10, 'b': 20}
        if add_to_self:
            expected2['conffile'] = []
        argv = argv1 + argv2

        parser = argparseconfig.ArgparseConfigParser(add_help=False)
        parsed, remaining, config, cfgparser = \
            parser.add_and_parse_config_files(
                '-c', '--conffile', args=argv, config_section='main',
                add_to_self=add_to_self)

        assert parser.config_parser == config
        self.assert_args_equal({'conffile': [str(cfg1), str(cfg2)]}, parsed)
        assert remaining == argv2
        assert config.sections() == ['main', 'subgroup']
        assert dict(config.items('main')) == {'a': '1'}
        assert dict(config.items('subgroup')) == {'b': '3'}

        parser.add_argument('-a', type=int)
        parser.add_argument('-b', type=int)
        parsed2 = parser.parse_args(remaining)

        self.assert_args_equal(expected2, parsed2)

    @pytest.mark.parametrize('mode', ['noargs', 'cmdargs', 'cfgfile'])
    def test_add_argument_with_action_type(self, tmpdir, mode):
        cfg1txt = [
            '[main]',
            'a = True',
            'b = False',
            'd = 1',
            'e = 0',
            'vs = 3',
        ]

        cfg1 = tmpdir.join('f1.cfg')
        cfg1.write('\n'.join(cfg1txt))

        if mode == 'noargs':
            argv = []
            expected = {'a': False, 'b': True, 'd': False, 'e': True, 'vs': None}
        elif mode == 'cmdargs':
            argv = ['-a', '-b', '-d', '-e', '-vv']
            expected = {'a': True, 'b': False, 'd': True, 'e': False, 'vs': 2}
        elif mode == 'cfgfile':
            argv = ['-c', str(cfg1)]
            expected = {'a': True, 'b': False, 'd': True, 'e': False, 'vs': 3}

        parser = argparseconfig.ArgparseConfigParser(add_help=False)
        parsed, remaining, config, cfgparser = \
            parser.add_and_parse_config_files(
                '-c', '--conffile', args=argv, config_section='main')

        parser.add_argument('-a', action='store_true')
        parser.add_argument('-b', action='store_false')
        parser.add_argument('-d', action='store_true')
        parser.add_argument('-e', action='store_false')
        parser.add_argument('-v', '--vs', action='count')
        parsed2 = parser.parse_args(remaining)

        self.assert_args_equal(expected, parsed2)

    @pytest.mark.parametrize('config', ['match', 'nomatch', 'none'])
    @pytest.mark.parametrize('default', [None, 1])
    def test_set_action_default_from_config(self, config, default):
        action = argparse.Action('--test', 'test', default=default)

        if config == 'match':
            cd = {'test': 2}
            expected = {'default': 2}
        elif config == 'nomatch':
            cd = {'other': 3}
            expected = {'default': default}
        else:
            cd = None
            expected = {'default': default}
        argparseconfig.set_action_default_from_config(action, cd)

        self.assert_args_contains(expected, action)

    @pytest.mark.parametrize('config', ['dict', 'parser'])
    @pytest.mark.parametrize('mode', ['noargs', 'args'])
    def test_subgroup(self, config, mode):
        if config == 'dict':
            acpargs = {'config_dict': dict(self.cp.items('main'))}
            subgargs = {'config_dict': dict(self.cp.items('subgroup1'))}
        else:
            acpargs = {'config_parser': self.cp, 'config_section': 'main'}
            subgargs = {'config_section': 'subgroup1'}

        parser = argparseconfig.ArgparseConfigParser(**acpargs)
        parser.add_argument('--int', type=int)

        subgroup1 = parser.add_argument_group('subgroup1', **subgargs)
        subgroup1.add_argument('--float', type=float)

        if mode == 'noargs':
            argv = []
            expected = {'int': 1, 'float': 2.3}
        elif mode == 'args':
            argv = ['--int', '2', '--float', '4.5']
            expected = {'int': 2, 'float': 4.5}

        args = parser.parse_args(argv)
        self.assert_args_equal(expected, args)

    @pytest.mark.parametrize('config', ['dict', 'parser'])
    @pytest.mark.parametrize('mode', ['noargs', 'nosubargs', 'args'])
    def test_subparser(self, config, mode):
        if config == 'dict':
            acpargs = {'config_dict': dict(self.cp.items('main'))}
            subpargs = {'config_dict': dict(self.cp.items('subparser1'))}
            subgargs = {'config_dict': dict(self.cp.items('subgroup1'))}
        else:
            acpargs = {'config_parser': self.cp, 'config_section': 'main'}
            subpargs = {'config_section': 'subparser1'}
            subgargs = {'config_section': 'subgroup1'}

        parser = argparseconfig.ArgparseConfigParser(**acpargs)
        parser.add_argument('--int', type=int)

        subparsers = parser.add_subparsers()
        subparser1 = subparsers.add_parser('subparser1', **subpargs)
        subparser1.add_argument('--string')

        subgroup1 = subparser1.add_argument_group('subgroup1', **subgargs)
        subgroup1.add_argument('--float', type=float)

        if mode == 'noargs':
            argv = []
            # argparse calls system.exit on failure
            expected = SystemExit
        elif mode == 'nosubargs':
            argv = ['--int', '2', 'subparser1']
            expected = {'int': 2, 'string': 'a string', 'float': 2.3}
        elif mode == 'args':
            argv = ['--int', '2', 'subparser1', '--string', 'zzz',
                    '--float', '4.5']
            expected = {'int': 2, 'string': 'zzz', 'float': 4.5}

        if expected == SystemExit:
            with pytest.raises(expected):
                args = parser.parse_args(argv)
        else:
            args = parser.parse_args(argv)
            self.assert_args_equal(expected, args)

    @pytest.mark.parametrize('ignore_missing', [True, False])
    @pytest.mark.parametrize('missing', [True, False])
    def test_get_set_config(self, ignore_missing, missing):
        acpargs = {'config_parser': self.cp, 'config_section': 'main'}
        if not ignore_missing:
            acpargs['ignore_missing'] = False
        if missing:
            acpargs['config_section'] = 'missing'

        if ignore_missing or not missing:
            parser = argparseconfig.ArgparseConfigParser(**acpargs)
            if missing:
                assert parser.config_dict == {}
            else:
                assert parser.config_dict == {'int': '1'}
        else:
            if missing:
                with pytest.raises(NoSectionError):
                    parser = argparseconfig.ArgparseConfigParser(**acpargs)
            else:
                parser = argparseconfig.ArgparseConfigParser(**acpargs)
                assert parser.config_dict == {'int': '1'}
