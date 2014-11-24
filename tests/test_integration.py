# -*- coding: utf-8 -*-
#
# This file is part of Invenio Client.
# Copyright (C) 2010, 2011, 2014 CERN.
#
# Invenio Client is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio Client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Unit tests for the invenio_connector script."""

import os

from unittest import TestCase

from invenio_client import InvenioConnector, InvenioConnectorAuthError

CFG_SITE_URL = 'http://invenio-demo.cern.ch'
CFG_SITE_SECURE_URL = 'https://invenio-demo.cern.ch'


class InvenioConnectorTest(TestCase):

    """Test function to get default values."""

    def test_remote_search(self):
        """InvenioConnector - remote search."""
        server = InvenioConnector(CFG_SITE_URL)
        result = server.search(p='ellis', of='id')
        self.assertTrue(len(list(result)) > 0,
                        'did not get remote search results from '
                        'http://invenio-demo.cern.ch')

    def test_search_collections(self):
        """InvenioConnector - collection search"""
        server = InvenioConnector(CFG_SITE_URL)
        result = server.search(p='', c=['Books'], of='id')
        self.assertTrue(len(list(result)) > 0,
                        'did not get collection search results.')

    def _test_search_remote_restricted_collections(self):
        """InvenioConnector - remote restricted collection search"""
        server = InvenioConnector(CFG_SITE_URL)
        search_params = dict(p='LBL-28106', c=['Theses'], of='id',
                             ssl_verify=False)
        self.assertRaises(InvenioConnectorAuthError, server.search,
                          **search_params)

        server = InvenioConnector(CFG_SITE_SECURE_URL, user='jekyll',
                                  password='j123ekyll')
        result = server.search(p='LBL-28106', c=['Theses'], of='id',
                               ssl_verify=False)
        self.assertTrue(len(list(result)) > 0,
                        'did not get restricted collection search results.')
