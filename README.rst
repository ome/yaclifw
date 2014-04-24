Yet Another CLI Framework
=========================

`yaclifw` is a framework for building CLI tools.


|Build Status|

Getting Started
---------------

For Python 2.6, you will need to install `argparse`_

::

    $ pip install argparse

With that, it's possible to execute yaclifw:

::

    $ python yaclifw/main.py

Pip installation
-----------------

To install the latest release of yaclifw use pip install:

::

    $ pip install yaclifw
    $ yaclifw

Extending yaclifw
-----------------

The easiest way to make use of yaclifw is by cloning the
repository and modifying the main.py method to include
your own commands.

License
-------

yaclifw is released under the GPL.

Copyright
---------

2013-2014, The Open Microscopy Environment

.. _argparse: http://pypi.python.org/pypi/argparse
.. |Build Status| image:: https://travis-ci.org/openmicroscopy/yaclifw.png
   :target: http://travis-ci.org/openmicroscopy/yaclifw
