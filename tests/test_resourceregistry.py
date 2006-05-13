#!/usr/bin/python
# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# - Anahide Tchertchian <at@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
#-------------------------------------------------------------------------------
# $Id$
"""Resource registry tests
"""

import unittest

from Products.CPSRelation.resourceregistry import ResourceRegistry

# register default resources
from Products.CPSRelation import node
from Products.CPSRelation.node import VersionResource
from Products.CPSRelation.node import VersionHistoryResource
from Products.CPSRelation.node import RpathResource

class DummyResource:
    prefix = "dummy"

class TestResourceRegistry(unittest.TestCase):

    def setUp(self):
        self.save_registry = ResourceRegistry._registry.copy()

    def tearDown(self):
        ResourceRegistry._registry = self.save_registry

    def test_listResourcePrefixes(self):
        res = list(ResourceRegistry.listResourcePrefixes())
        res.sort()
        self.assertEquals(res, ['docid', 'rpath', 'uuid'])

    def test_register(self):
        ResourceRegistry.register(DummyResource)
        self.assertEquals("dummy" in ResourceRegistry.listResourcePrefixes(),
                          True)

    def test_makeResource(self):
        # localname ids needed for prefixed resources
        res = ResourceRegistry.makeResource('docid', localname='12345')
        self.assertEquals(res, VersionHistoryResource('12345'))
        res = ResourceRegistry.makeResource('uuid', localname='',
                                            docid='12345', revision=1)
        self.assertEquals(res, VersionResource(docid='12345', revision=1))
        res = ResourceRegistry.makeResource('uuid', localname='12345__0001')
        self.assertEquals(res, VersionResource(docid='12345', revision=1))
        res = ResourceRegistry.makeResource('rpath',
                                            localname='workspaces/toto')
        self.assertEquals(res, RpathResource('workspaces/toto'))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestResourceRegistry))
    return suite

