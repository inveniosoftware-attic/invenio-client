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

"""CERN Document Server specific connector."""

import splinter
from invenio_client import InvenioConnector


class CDSInvenioConnector(InvenioConnector):

    __url__ = "http://cds.cern.ch/"

    def __init__(self, user="", password=""):
        """Use to connect to the CERN Document Server (CDS).

        .. note:: It uses centralized SSO for authentication.
        """
        cds_url = self.__url__
        if user:
            cds_url = cds_url.replace('http', 'https')
        super(CDSInvenioConnector, self).__init__(
            cds_url, user, password)

    def _init_browser(self):
        """Update this everytime the CERN SSO login form is refactored."""
        self.browser = splinter.Browser('phantomjs')
        self.browser.visit(self.server_url)
        self.browser.find_link_by_partial_text("Sign in").click()
        self.browser.fill(
            'ctl00$ctl00$NICEMasterPageBodyContent$SiteContentPlaceholder$'
            'txtFormsLogin', self.user)
        self.browser.fill(
            'ctl00$ctl00$NICEMasterPageBodyContent$SiteContentPlaceholder$'
            'txtFormsPassword', self.password)
        self.browser.find_by_css('input[type=submit]').click()
        self.browser.find_by_css('input[type=submit]').click()

__all__ = ('CDSInvenioConnector', )
