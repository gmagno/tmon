.. highlight:: shell

============
Installation
============


Stable release
--------------

To install Temp Monitor, run this command in your terminal:

.. code-block:: console

    $ pip install tmonpy

This is the preferred method to install Temp Monitor, as it will always install
the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


Alternatively a `tmon` binary (AppImage) may be downloaded from the releases
page:

.. code-block:: console

    $ # replace ??????? by the actual hash
    $ wget https://github.com/gmagno/tmon/releases/latest/download/tmon-???????-x86_64.AppImage
    $ chmod +x tmon-*-x86_64.AppImage


From sources
------------

The sources for Temp Monitor can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/gmagno/tmon

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/gmagno/tmon/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/gmagno/tmon
.. _tarball: https://github.com/gmagno/tmon/tarball/master
