# -*- coding: utf-8 -*-
#
# This file is part of Invenio-Client.
# Copyright (C) 2014 CERN.
#
# Invenio-Client is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio-Client is distributed in the hope that it will be useful,
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

"""Unit tests for the utils/connector."""

from unittest import TestCase

from invenio_client import InvenioConnector, InvenioConnectorServerError


class TestConnector(TestCase):

    """Test function to get default values."""

    def test_url_errors(self):
        """InvenioConnector - URL errors"""
        invalid_urls = [
            'htp://cds.cern.ch',
            'cds.cern.ch',
            'http://thecerndocumentserver.cern.ch',
            'invalidurl',
            'http://mgfldgmdflgmdfklgmklmkdflg.com'
        ]
        for url in invalid_urls:
            self.assertRaises(InvenioConnectorServerError,
                              InvenioConnector, url)
