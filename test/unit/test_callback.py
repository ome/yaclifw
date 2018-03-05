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

from __future__ import absolute_import
import argparse

from yaclifw.framework import main
from yaclifw.framework import Command


class Listener(object):

    def __init__(self):
        self.calls = set()

    def called(self, value):
        self.calls.add(value)


LISTENER = Listener()


class CallbackCommand(Command):

    NAME = "cb"

    def __init__(self, *args, **kwargs):
        super(CallbackCommand, self).__init__(*args, **kwargs)
        self.parser.add_argument(
            '--callback', default=self.cb, help=argparse.SUPPRESS)

    def __call__(self, *args, **kwargs):
        LISTENER.called("call")

    def cb(self):
        LISTENER.called("cb")


class TestCallback(object):

    def testCallback(self, capsys):
        main("test", ["cb"], items=[("cb", CallbackCommand)])
        out, err = capsys.readouterr()
        assert LISTENER.calls == set(["call", "cb"])
