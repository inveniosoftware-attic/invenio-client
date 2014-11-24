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

"""Tool to connect to distant Invenio servers using Invenio APIs.

Example of use:

.. code-block:: python

    from invenio_client import InvenioConnector
    demo = InvenioConnector("http://invenio-demo.cern.ch")

    results = demo.search("higgs")

    for record in results:
        print record["245__a"][0]
        print record["520__b"][0]
        for author in record["100__"]:
            print author["a"][0], author["u"][0]

FIXME:

- implement cache expiration
- exceptions handling
- parsing of ``<!-- Search-Engine-Total-Number-Of-Results: N -->``
- better checking of input parameters
"""

from __future__ import print_function

import os
import re
import requests
import json
import splinter
import sys
import tempfile
import time
import urllib
import urllib2
import xml.sax

from requests.exceptions import (ConnectionError, InvalidSchema, InvalidURL,
                                 MissingSchema, RequestException)

from ._compat import binary_type
from .version import __version__

CFG_USER_AGENT = "invenio_connector"


class InvenioConnectorError(Exception):

    """General connector error."""

    def __init__(self, value):
        """Set the internal "value" attribute."""
        super(InvenioConnectorError, self).__init__()
        self.value = value

    def __str__(self):
        """Return oneself as a string based on self.value."""
        return str(self.value)


class InvenioConnectorAuthError(InvenioConnectorError):

    """Failed authentication during remote connections."""


class InvenioConnectorServerError(InvenioConnectorError):

    """Problem with connecting to Invenio server."""


class InvenioConnector(object):

    """Create an connector to a server running Invenio."""

    def __init__(self, url, user="", password="", login_method="Local",
                 insecure_login=False):
        """
        Initialize a new instance of the server at given URL.

        If the server happens to be running on the local machine, the
        access will be done directly using the Python APIs. In that case
        you can choose from which base path to import the necessary file
        specifying the local_import_path parameter.

        :param url: the url to which this instance will be connected.
            Defaults to CFG_SITE_URL, if available.
        :type url: string
        :param user: the optional username for interacting with the Invenio
            instance in an authenticated way.
        :type user: string
        :param password: the corresponding password.
        :type password: string
        :param login_method: the name of the login method the Invenio instance
            is expecting for this user (in case there is more than one).
        :type login_method: string
        """
        assert url is not None
        self.server_url = url
        self._validate_server_url()

        self.cached_queries = {}
        self.cached_records = {}
        self.cached_baskets = {}
        self.user = user
        self.password = password
        self.login_method = login_method
        self.browser = None
        self.cookies = {}
        if self.user:
            if not insecure_login and \
                    not self.server_url.startswith('https://'):
                raise InvenioConnectorAuthError(
                    "You have to use a secure URL (HTTPS) to login")
            self._init_browser()
            self._check_credentials()

    def _init_browser(self):
        """Overide in appropriate way to prepare a logged in browser."""
        self.browser = splinter.Browser('phantomjs')
        self.browser.visit(self.server_url + "/youraccount/login")
        try:
            self.browser.fill('nickname', self.user)
            self.browser.fill('password', self.password)
        except:
            self.browser.fill('p_un', self.user)
            self.browser.fill('p_pw', self.password)
        self.browser.fill('login_method', self.login_method)
        self.browser.find_by_css('input[type=submit]').click()

    def _check_credentials(self):
        if not len(self.browser.cookies.all()):
            raise InvenioConnectorAuthError(
                "It was not possible to successfully login with "
                "the provided credentials")
        self.cookies = self.browser.cookies.all()

    def search(self, read_cache=True, ssl_verify=True, **kwparams):
        """
        Returns records corresponding to the given search query.

        See docstring of invenio.legacy.search_engine.perform_request_search()
        for an overview of available parameters.
        """
        parse_results = False
        of = kwparams.get('of', "")
        if of == "":
            parse_results = True
            of = "xm"
            kwparams['of'] = of
        params = kwparams
        cache_key = (json.dumps(params), parse_results)

        if cache_key not in self.cached_queries or \
                not read_cache:
            results = requests.get(self.server_url + "/search",
                                   params=params, cookies=self.cookies,
                                   stream=True, verify=ssl_verify)
            if 'youraccount/login' in results.url:
                # Current user not able to search collection
                raise InvenioConnectorAuthError(
                    "You are trying to search a restricted collection. "
                    "Please authenticate yourself.\n")
        else:
            return self.cached_queries[cache_key]

        if parse_results:
            # FIXME: we should not try to parse if results is string
            parsed_records = self._parse_results(results.raw,
                                                 self.cached_records)
            self.cached_queries[cache_key] = parsed_records
            return parsed_records
        else:
            # pylint: disable=E1103
            # The whole point of the following code is to make sure we can
            # handle two types of variable.
            try:
                res = results.content
            except AttributeError:
                res = results
            # pylint: enable=E1103

            if of == "id":
                try:
                    if isinstance(res, binary_type):
                        # Transform to list
                        res = [int(recid.strip()) for recid in
                               res.decode('utf-8').strip("[]").split(",")
                               if recid.strip() != ""]
                    res.reverse()
                except (ValueError, AttributeError):
                    res = []
            self.cached_queries[cache_key] = res
            return res

    def search_with_retry(self, sleeptime=3.0, retrycount=3, **params):
        """Perform a search given a dictionary of ``search(...)`` parameters.

        It accounts for server timeouts as necessary and will retry some number
        of times.

        :param sleeptime: number of seconds to sleep between retries
        :param retrycount: number of times to retry given search
        :param params: search parameters
        :return: records in given format
        """
        results = []
        count = 0
        while count < retrycount:
            try:
                results = self.search(**params)
                break
            except urllib2.URLError:
                sys.stderr.write("Timeout while searching...Retrying\n")
                time.sleep(sleeptime)
                count += 1
        else:
            sys.stderr.write(
                "Aborting search after %d attempts.\n" % (retrycount,))
        return results

    def search_similar_records(self, recid):
        """Return the records similar to the given one."""
        return self.search(p="recid:" + str(recid), rm="wrd")

    def search_records_cited_by(self, recid):
        """Return records cited by the given one."""
        return self.search(p="recid:" + str(recid), rm="citation")

    def get_records_from_basket(self, bskid, group_basket=False,
                                read_cache=True):
        """
        Returns the records from the (public) basket with given bskid
        """
        if bskid not in self.cached_baskets or not read_cache:
            if self.user:
                if group_basket:
                    group_basket = '&category=G'
                else:
                    group_basket = ''
                results = requests.get(
                    self.server_url + "/yourbaskets/display?of=xm&bskid=" +
                    str(bskid) + group_basket, cookies=self.cookies,
                    stream=True)
            else:
                results = requests.get(
                    self.server_url +
                    "/yourbaskets/display_public?of=xm&bskid=" + str(bskid),
                    stream=True)
        else:
            return self.cached_baskets[bskid]

        parsed_records = self._parse_results(results.raw, self.cached_records)
        self.cached_baskets[bskid] = parsed_records
        return parsed_records

    def get_record(self, recid, read_cache=True):
        """
        Returns the record with given recid
        """
        if recid in self.cached_records or not read_cache:
            return self.cached_records[recid]
        else:
            return self.search(p="recid:" + str(recid))

    def upload_marcxml(self, marcxml, mode):
        """
        Uploads a record to the server

        Parameters:
          marcxml - *str* the XML to upload.
             mode - *str* the mode to use for the upload.
                    "-i" insert new records
                    "-r" replace existing records
                    "-c" correct fields of records
                    "-a" append fields to records
                    "-ir" insert record or replace if it exists
        """
        if mode not in ["-i", "-r", "-c", "-a", "-ir"]:
            raise NameError("Incorrect mode " + str(mode))

        params = urllib.urlencode({'file': marcxml,
                                   'mode': mode})
        # We don't use self.browser as batchuploader is protected by IP
        opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', CFG_USER_AGENT)]
        return opener.open(self.server_url + "/batchuploader/robotupload",
                           params)

    def _parse_results(self, results, cached_records):
        """
        Parses the given results (in MARCXML format).

        The given "cached_records" list is a pool of
        already existing parsed records (in order to
        avoid keeping several times the same records in memory)
        """
        parser = xml.sax.make_parser()
        handler = RecordsHandler(cached_records)
        parser.setContentHandler(handler)
        parser.parse(results)
        return handler.records

    def _validate_server_url(self):
        """Validates self.server_url"""
        try:
            request = requests.head(self.server_url)
            if request.status_code >= 400:
                raise InvenioConnectorServerError(
                    "Unexpected status code '%d' accessing URL: %s"
                    % (request.status_code, self.server_url))
        except (InvalidSchema, MissingSchema) as err:
            raise InvenioConnectorServerError(
                "Bad schema, expecting http:// or https://:\n %s" % (err,))
        except ConnectionError as err:
            raise InvenioConnectorServerError(
                "Couldn't establish connection to '%s':\n %s"
                % (self.server_url, err))
        except InvalidURL as err:
            raise InvenioConnectorServerError(
                "Invalid URL '%s':\n %s"
                % (self.server_url, err))
        except RequestException as err:
            raise InvenioConnectorServerError(
                "Unknown error connecting to '%s':\n %s"
                % (self.server_url, err))


class Record(dict):

    """Represent an Invenio record."""

    def __init__(self, recid=None, marcxml=None, server_url=None):
        self.recid = recid
        self.marcxml = ""
        if marcxml is not None:
            self.marcxml = marcxml
        self.server_url = server_url

    def __setitem__(self, item, value):
        tag, ind1, ind2, subcode = decompose_code(item)
        if subcode is not None:
            super(Record, self).__setitem__(
                tag + ind1 + ind2, [{subcode: [value]}])
        else:
            super(Record, self).__setitem__(tag + ind1 + ind2, value)

    def __getitem__(self, item):
        tag, ind1, ind2, subcode = decompose_code(item)

        datafields = dict.__getitem__(self, tag + ind1 + ind2)
        if subcode is not None:
            subfields = []
            for datafield in datafields:
                if subcode in datafield:
                    subfields.extend(datafield[subcode])
            return subfields
        else:
            return datafields

    def __contains__(self, item):
        return super(Record, self).__contains__(item)

    def __repr__(self):
        return "Record(" + dict.__repr__(self) + ")"

    def __str__(self):
        return self.marcxml

    def export(self, of="marcxml"):
        """
        Returns the record in chosen format
        """
        return self.marcxml

    def url(self):
        """
        Returns the URL to this record.
        Returns None if not known
        """
        if self.server_url is not None and \
                self.recid is not None:
            return '/'.join(
                [self.server_url, CFG_SITE_RECORD, str(self.recid)])
        else:
            return None


class RecordsHandler(xml.sax.handler.ContentHandler):

    "MARCXML Parser"

    def __init__(self, records):
        """Initialize MARCXML Parser.

        :param records: dictionary with an already existing cache of records
        """
        self.cached_records = records
        self.records = []
        self.in_record = False
        self.in_controlfield = False
        self.in_datafield = False
        self.in_subfield = False
        self.cur_tag = None
        self.cur_subfield = None
        self.cur_controlfield = None
        self.cur_datafield = None
        self.cur_record = None
        self.recid = 0
        self.buffer = ""
        self.counts = 0

    def startElement(self, name, attributes):
        if name == "record":
            self.cur_record = Record()
            self.in_record = True

        elif name == "controlfield":
            tag = attributes["tag"]
            self.cur_datafield = ""
            self.cur_tag = tag
            self.cur_controlfield = []
            if tag not in self.cur_record:
                self.cur_record[tag] = self.cur_controlfield
            self.in_controlfield = True

        elif name == "datafield":
            tag = attributes["tag"]
            self.cur_tag = tag
            ind1 = attributes["ind1"]
            if ind1 == " ":
                ind1 = "_"
            ind2 = attributes["ind2"]
            if ind2 == " ":
                ind2 = "_"
            if tag + ind1 + ind2 not in self.cur_record:
                self.cur_record[tag + ind1 + ind2] = []
            self.cur_datafield = {}
            self.cur_record[tag + ind1 + ind2].append(self.cur_datafield)
            self.in_datafield = True

        elif name == "subfield":
            subcode = attributes["code"]
            if subcode not in self.cur_datafield:
                self.cur_subfield = []
                self.cur_datafield[subcode] = self.cur_subfield
            else:
                self.cur_subfield = self.cur_datafield[subcode]
            self.in_subfield = True

    def characters(self, data):
        if self.in_subfield:
            self.buffer += data
        elif self.in_controlfield:
            self.buffer += data
        elif "Search-Engine-Total-Number-Of-Results:" in data:
            print(data)
            match_obj = re.search("\d+", data)
            if match_obj:
                print(int(match_obj.group()))
                self.counts = int(match_obj.group())

    def endElement(self, name):
        if name == "record":
            self.in_record = False
        elif name == "controlfield":
            if self.cur_tag == "001":
                self.recid = int(self.buffer)
                if self.recid in self.cached_records:
                    # Record has already been parsed, no need to add
                    pass
                else:
                    # Add record to the global cache
                    self.cached_records[self.recid] = self.cur_record
                # Add record to the ordered list of results
                self.records.append(self.cached_records[self.recid])

            self.cur_controlfield.append(self.buffer)
            self.in_controlfield = False
            self.buffer = ""
        elif name == "datafield":
            self.in_datafield = False
        elif name == "subfield":
            self.in_subfield = False
            self.cur_subfield.append(self.buffer)
            self.buffer = ""


def decompose_code(code):
    """Decompose a MARC "code" into tag, ind1, ind2, subcode."""
    code = "%-6s" % code
    ind1 = code[3:4]
    if ind1 == " ":
        ind1 = "_"
    ind2 = code[4:5]
    if ind2 == " ":
        ind2 = "_"
    subcode = code[5:6]
    if subcode == " ":
        subcode = None
    return (code[0:3], ind1, ind2, subcode)
