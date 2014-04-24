Yet Another CLI Framework
=========================

|Build Status|

Introduction
------------

`yaclifw` is a framework for building CLI tools.

Dependencies
------------

Direct dependencies of yaclifw are:

- `argparse`_

Installation
------------

To install ``yaclifw``, run::

 $ python setup.py install

or using pip, run::

 $ pip install yaclifw

To upgrade your pip installation, run::

 $ pip install -U yaclifw

Usage
-----

The list of available commands can be listed with::

  $ yaclifw -h

For each subcommand, additional help can be queried, e.g.::

  $ yaclifw example -h

Extending yaclifw
-----------------

The easiest way to make use of yaclifw is by cloning the
repository and modifying the main.py method to include
your own commands.

Contributing
------------

yaclifw follows `PEP 8`_, the Style Guide for Python Code. Please check your
code with pep8_ or flake8_, the Python style guide checkers, by running
``flake8 -v .`` or ``pep8 -v .``.

.. _PEP 8: http://www.python.org/dev/peps/pep-0008/


Running tests
-------------

The tests are located under the `test` directory. To run all the tests, use
the `test` target of `setup.py`::

  python setup.py test

Unit tests
^^^^^^^^^^

Unit tests are stored under the `test/unit` folder and can be run by calling::

  python setup.py test -s test/unit

Unit tests are also run by the Travis_ build on every Pull Request opened
against the main repository.

License
-------

yaclifw is released under the GPL.

Copyright
---------

2014, The Open Microscopy Environment

.. _argparse: http://pypi.python.org/pypi/argparse
.. _pep8: https://pypi.python.org/pypi/pep8
.. _flake8: https://pypi.python.org/pypi/flake8
.. _Travis: http://travis-ci.org/openmicroscopy/yaclifw

.. |Build Status| image:: https://travis-ci.org/openmicroscopy/yaclifw.png
   :target: http://travis-ci.org/openmicroscopy/yaclifw
