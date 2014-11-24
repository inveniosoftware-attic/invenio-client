# -*- coding: utf-8 -*-
#
# This file is part of Invenio Client.
# Copyright (C) 2014 CERN.
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

"""CERN Document Server specific connector."""

import mechanize

from invenio_client import InvenioConnector


class _SGMLParserFactory(mechanize.DefaultFactory):

    """Black magic to be able to interact with CERN SSO forms."""

    def __init__(self, i_want_broken_xhtml_support=False):
        forms_factory = mechanize.FormsFactory(
            form_parser_class=mechanize.XHTMLCompatibleFormParser)
        mechanize.Factory.__init__(
            self,
            forms_factory=forms_factory,
            links_factory=mechanize.LinksFactory(),
            title_factory=mechanize.TitleFactory(),
            response_type_finder=mechanize._html.ResponseTypeFinder(
                allow_xhtml=i_want_broken_xhtml_support),
        )


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
        self.browser = mechanize.Browser(
            factory=_SGMLParserFactory(i_want_broken_xhtml_support=True))
        self.browser.set_handle_robots(False)
        self.browser.open(self.server_url)
        self.browser.follow_link(text_regex="Sign in")
        self.browser.select_form(nr=0)
        self.browser.form[
            'ctl00$ctl00$NICEMasterPageBodyContent$SiteContentPlaceholder$'
            'txtFormsLogin'] = self.user
        self.browser.form[
            'ctl00$ctl00$NICEMasterPageBodyContent$SiteContentPlaceholder$'
            'txtFormsPassword'] = self.password
        self.browser.submit()
        self.browser.select_form(nr=0)
        self.browser.submit()

__all__ = ('CDSInvenioConnector', )
