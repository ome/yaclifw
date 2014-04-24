#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2013-2014 University of Dundee & Open Microscopy Environment
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

import os
import pytest

from yaclifw import __file__ as module_file
from yaclifw.framework import main
from yaclifw.version import call_git_describe
from yaclifw.version import get_git_version
from yaclifw.version import _lookup_version
from yaclifw.version import Version


version_dir, version_file = _lookup_version(module_file)


class TestVersion(object):

    def setup_method(self, method):
        if os.path.isfile(version_file):
            os.rename(version_file, version_file + '.bak')
        assert not os.path.isfile(version_file)

    def teardown_method(self, method):
        if os.path.isfile(version_file + '.bak'):
            os.rename(version_file + '.bak', version_file)

    def read_version_file(self):
        version = None
        with open(version_file) as f:
            version = f.readlines()[0]
        return version.strip()

    @pytest.mark.xfail
    def testVersionOutput(self, capsys):
        main("test", ["version"], items=[("version", Version)])
        out, err = capsys.readouterr()
        assert out.rstrip() == get_git_version(module_file)

    @pytest.mark.xfail
    def testVersionFile(self, capsys):
        main("test", ["version"], items=[("version", Version)])
        assert os.path.isfile(version_file)
        out, err = capsys.readouterr()
        assert out.rstrip() == self.read_version_file()

    @pytest.mark.xfail
    def testVersionOverwrite(self, capsys):
        with open(version_file, 'w') as f:
            f.write('test\n')
        assert self.read_version_file() == 'test'
        try:
            main("test", ["version"], items=[("version", Version)])
            out, err = capsys.readouterr()
            assert out.rstrip() == self.read_version_file()
        finally:
            os.remove(version_file)

    @pytest.mark.xfail
    def testNonGitRepository(self, capsys):
        # Move to a non-git repository and ensure call_git_describe
        # returns None
        dir = os.getcwd()
        os.chdir('..')
        try:
            assert call_git_describe() is None
            main("test", ["version"], items=[("version", Version)])
            out, err = capsys.readouterr()
            assert out.rstrip() == self.read_version_file()
        except:
            os.chdir(dir)

    @pytest.mark.xfail
    def testGitRepository(self, tmpdir):
        cwd = os.getcwd()
        from subprocess import Popen, PIPE
        sandbox_url = "https://github.com/openmicroscopy/snoopys-sandbox.git"
        path = str(tmpdir.mkdir("sandbox"))
        # Read the version for the current Git repository
        main("test", ["version"], items=[("version", Version)])
        version = self.read_version_file()
        try:
            # Clone snoopys-sanbox
            p = Popen(["git", "clone", sandbox_url, path],
                      stdout=PIPE, stderr=PIPE)
            assert p.wait() == 0
            os.chdir(path)
            # Check git describe returns a different version number
            assert call_git_describe() != version
            # Read the version again and check the file is unmodified
            main("test", ["version"], items=[("version", Version)])
            assert self.read_version_file() == version
        finally:
            os.chdir(cwd)

    @pytest.mark.parametrize('prefix', ['', 'v'])
    @pytest.mark.parametrize('suffix', ['', '-rc1', '-31-gbf8afc8'])
    def testVersionNumber(self, capsys, monkeypatch, prefix, suffix):
        def mockreturn(abbrev):
                return '%s0.0.0%s' % (prefix, suffix)
        import yaclifw.version
        monkeypatch.setattr(yaclifw.version, 'call_git_describe', mockreturn)
        version = get_git_version(module_file)
        assert version == '0.0.0%s' % suffix

    @pytest.mark.parametrize(('prefix', 'suffix'), [['', 'rc1'], ['v.', '']])
    def testInvalidVersionNumber(self, capsys, monkeypatch, prefix, suffix):
        def mockreturn(abbrev):
                return '%s0.0.0%s' % (prefix, suffix)
        import yaclifw.version
        monkeypatch.setattr(yaclifw.version, 'call_git_describe', mockreturn)
        with pytest.raises(ValueError):
            get_git_version(module_file)
