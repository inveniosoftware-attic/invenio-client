..
    This file is part of Invenio-Client
    Copyright (C) 2014, 2016 CERN.

    Invenio-Client is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio-Client is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio-Client; if not, write to the Free Software Foundation,
    Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

    In applying this licence, CERN does not waive the privileges and immunities
    granted to it by virtue of its status as an Intergovernmental Organization
    or submit itself to any jurisdiction.

================
 Invenio-Client
================
.. currentmodule:: invenio_client

.. raw:: html

    <p style="height:22px; margin:0 0 0 2em; float:right">
        <a href="https://travis-ci.org/inveniosoftware/invenio-client">
            <img src="https://travis-ci.org/inveniosoftware/invenio-client.png?branch=master"
                 alt="travis-ci badge"/>
        </a>
        <a href="https://coveralls.io/r/inveniosoftware/invenio-client">
            <img src="https://coveralls.io/repos/inveniosoftware/invenio-client/badge.png?branch=master"
                 alt="coveralls.io badge"/>
        </a>
    </p>

Invenio-Client is a Python library permitting to connect to remote
`Invenio <http://inveniosoftware.org>`_ digital library instances.

Contents
--------

.. contents::
   :local:
   :backlinks: none


Installation
============

Invenio-Client is on PyPI so all you need is:

.. code-block:: console

    $ pip install invenio-client


Usage
=====

The easiest way is to use *invenio_client* directly with
:class:`~invenio_client.connector.InvenioConnector`.

.. code-block:: python

    from invenio_client import InvenioConnector
    demo = InvenioConnector("http://demo.inveniosoftware.org")

    results = demo.search("higgs")

    for record in results:
        print record["245__a"][0]
        print record["520__b"][0]
        for author in record["100__"]:
            print author["a"][0], author["u"][0]


API
===

.. automodule:: invenio_client.connector
   :members:

.. automodule:: invenio_client.contrib.cds
   :members:
   :undoc-members:

.. include:: ../CHANGES.rst

.. include:: ../CONTRIBUTING.rst

..
    License
    =======
    .. include:: ../LICENSE

.. include:: ../AUTHORS.rst
