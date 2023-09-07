pfmongo
=======

.. image:: https://badge.fury.io/py/pfmongo.svg
    :target: https://badge.fury.io/py/pfmongo

.. image:: https://travis-ci.org/FNNDSC/pfmongo.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/pfmongo

.. image:: https://img.shields.io/badge/python-3.5%2B-blue.svg
    :target: https://badge.fury.io/py/pfmongo

.. contents:: Table of Contents


Quick Overview
--------------

``pfmongo`` is a python client/module (CLI and API) for simplifying the interaction with a MongoDB. The module provides some *idiosyncratic* abstractions that are nonetheless hoped to be logically straightforward. The repository includes a ``docker-compose.yml`` that allows for easy instantiation of the MongoDB infrastructure.

Warning, Will Robinson!
-----------------------

If you wish to use ``pfmongo`` on your own computer, you do need to note these prerequisites:

``docker`` and ``docker-compose``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since ``pfmongo`` interacts with a MongoDB, the easiest mechanism to deploy this database is via ``docker-compose`` and hence ``docker``. Installation of these is beyond the scope of this document, but should be straightforward enough. Google is your friend in that quest.


Overview
--------

``pfmongo`` provides a somewhat opinionated abstraction for interacting with a MongoDB.


Installation
------------

Using ``PyPI``
~~~~~~~~~~~~~~

The best method of installing this script and all of its dependencies is by fetching it from PyPI using `a python virtual environment <https://medium.com/swlh/how-to-setup-your-python-projects-1eb5108086b1>`_.

.. code:: bash

        pip3 install pfmongo

Using CLI
~~~~~~~~~

Alternatively, from a cloned version of the repository:

.. code:: bash

        pip3 install -r requirements.txt -U ./


Running
-------

Ecosystem
~~~~~~~~~

Assuming you have `docker` and `docker-compose` on your system, do

.. code:: bash

    docker-compose up -d

Environment
~~~~~~~~~~~

Several environment variables need to be set prior to running ``persair``:

Linux
^^^^^

.. code:: bash

    export MD_DB=tanguro && export DBauthPath=/home/dicom/services/pfair.json &&\
    export MD_URI=mongodb://localhost:27017 && export ReadWriteKey=tanguro

In the above, the ``/home/dicom/services/pfair.json`` is the full path of the key-file you might have created earlier. Obviously, your location will vary. For the case of Windows, use Windows Powershell and

Windows
^^^^^^^

.. code:: bash

    $env:MD_DB=tanguro
    $env:DBauthPath=C:\users\me\key.json
    $env:MD_URI=mongodb://localhost:27017
    $env:ReadWriteKey=tanguro


Command line arguments
----------------------

.. code:: console

        [--mongodbinit <init.json>]
        The mongodb initialization file.

        [--version]
        If specified, print app name/version.

        [--man]
        If specified, print this help/man page.

        [--useDB <DBname>]
        Use the data base called <DBname>.

        [--useCollection <collectionName>]
        Use the collection called <collectionName>.

        [--addDocument <document.json>]
        Add the <document.json> to the <DBname>/<collectionName>.

        [--searchOn <searchExp>]
        Search for <searchExp> (see below) in the <DBname>/<collectionName>.
        
Examples
--------

- Coming soon:

.. code:: bash

  pfmongo --addDocument data.json


*-30-*
