#!/usr/bin/env python
#
# This file is part of Invenio-Client.
# Copyright (C) 2014, 2015, 2016 CERN.
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

"""Command line client for Invenio."""

import os
import re
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

setup_requires = [
    'pytest-runner>=2.6.2',
]

# Get the version string.  Cannot be done with import!
with open(os.path.join('invenio_client', 'version.py'), 'rt') as f:
    version = re.search(
        '__version__\s*=\s*"(?P<version>.*)"\n',
        f.read()
    ).group('version')

tests_require = [
    'pytest-cache>=1.0',
    'pytest-cov>=2.1.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
    'coverage>=4.0.0'
]

setup(
    name="invenio-client",
    version=version,
    url="https://github.com/inveniosoftware/invenio-client",
    license='GPLv2',
    author='Invenio collaboration',
    author_email='info@inveniosoftware.org',
    description="Invenio-Client permits to connect to remote Invenio digital "
        "library instances.",
    long_description=__doc__,
    packages=find_packages(exclude=["tests", "docs"]),
    include_package_data=True,
    install_requires=[
        'requests',
        'splinter',
        'click',
    ],
    extras_require={
        "docs": ["sphinx_rtd_theme"],
        "tests": tests_require,
    },
    tests_require=tests_require,
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 '
        'or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
)
