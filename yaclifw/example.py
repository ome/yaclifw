#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from framework import Command

log = logging.getLogger("yaclifw.example")


class ExampleCommand(Command):
    """
    Example command for yaclifw
    """

    NAME = "example"

    def __init__(self, sub_parsers):
        super(ExampleCommand, self).__init__(sub_parsers)

        self.parser.add_argument("-n", "--dry-run", action="store_true")

    def __call__(self, args):
        super(ExampleCommand, self).__call__(args)
        self.configure_logging(args)
        self.log.debug("debug")
        self.log.info("info")
