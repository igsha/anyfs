About the project
=================

A fuse-based filesystem that get structure from the executable script.

How to install
--------------

This application is a python package.
You can use ``pip`` to install it directly from github:

.. code-block:: sh

  $ pip install https://github.com/igsha/anyfs/tarball/master

Another option is to use `nix <https://nixos.org/guides/install-nix.html>`_:

.. code-block:: sh

  $ nix profile install github:igsha/anyfs#

How to use
----------

Mount
~~~~~

Like any fuse-based filesystem ``anyfs`` should be started as

.. code-block:: sh

  $ anyfs /mount/point -c <cmd>

Parameters:

* ``/mount/point`` A folder where the program should mount data.

Unmount
~~~~~~~

To unmount the mount point just use

.. code-block:: sh

  $ fusermount -u /mount/point

Protocol
--------

``anyfs`` communicates with resource via stdin and stdout.
Resource is a script or binary program that provides a directory structure.

``anyfs`` sends the path of the file or directory to stdin.
The answer on stdout is a sequence of commands from the table below that ends with ``eom`` command.
Each command can have additional argument ``time=N`` which represents a unix timestamp.
Timestamps for the directories are the minimal timestamp value of contained files.
Also there is a ``hide=true`` argument which allows to hide file on the directory level (the ``readdir``
fuse command will not list this file).

.. list-table:: Supported commands
  :header-rows: 1

  * - Command
    - Description

  * - .. code-block::

        bytes count=N path=/path/to/file
        <raw bytes>

    - Send ``N`` ``raw bytes``.

  * - .. code-block::

        entity path=/path/to/file

    - Forward declaration of directory of file.

  * - .. code-block::

        url headers=H count=N path=/path/to/file
        header1: value1
        header2: value2
        ...
        headerH: valueH
        ...
        url1
        url2
        ...
        urlN

    - Send `N` urls: it will be used the next url if the previous one returns 404.
      Also it can be sent `H` headers fields.

  * - .. code-block::

        link path=/path/to/file
        /real/path/to/file

    - Link ``/real/path/path/to/file`` by ``/path/to/file``.
      All paths should be absolute.

  * - .. code-block::

        notfound path=/path/to/file

    - The requested path has not been found.

  * - .. code-block::

        ioerror path=/path/to/file

    - The requested path caused an I/O error.

Backus-Naur form.

.. code::

   message := command+ 'eom\n'
   command := bytes | entity | url | link | notfound | ioerror
   bytes := 'bytes' time? hide? count path '\n' <raw data> '\n'
   entity := 'entity' time? hide? path '\n'
   url := 'url' time? hide? ('headers=' int)? count path '\n' <headers '\n'>* <urls '\n'>+
   link := 'link' time? hide? path '\n' <real path>
   notfound := 'notfound' path '\n'
   ioerror := 'ioerror' path '\n'
   time := 'time=' int
   count := 'count=' int
   path := 'path=' str
   hide := 'hide=true'
   int := [1-9][0-9]*
   str := [^\n]+

The ``path=`` argument should be always the last argument of a command.
Other arguments can be passed in any order.

The insides
-----------

The command ``url`` should contain bytes request.
The ``anyfs`` will try to request ranges from the URL using ``Range`` header and save the result in a local temporary file.
Local temporary files will be deleted after ``anyfs`` termination.
