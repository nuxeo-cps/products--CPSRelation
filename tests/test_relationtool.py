#!/usr/bin/python
# Copyright (c) 2004-2005 Nuxeo SARL <http://nuxeo.com>
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
#-------------------------------------------------------------------------------
"""Tests for Relations Tool
"""

import os
import unittest

from zope.interface.verify import verifyClass

from Products.CPSRelation.relationtool import RelationTool
from Products.CPSRelation.interfaces import IRelationTool
from Products.CPSRelation.tests.CPSRelationTestCase import CPSRelationTestCase
from Products.CPSRelation.tests.test_graphregistry import DEFAULT_GRAPH_TYPES


class TestRelationTool(CPSRelationTestCase):
    """Test Relations Tool with and iobtree graph
    """

    def setUp(self):
        CPSRelationTestCase.setUp(self)
        self.rtool = RelationTool()

    def test_interface(self):
        verifyClass(IRelationTool, RelationTool)

    def test_creation(self):
        tool = RelationTool()
        self.assertEqual(tool.getId(), 'portal_relations')
        self.assertEqual(tool.meta_type, 'Relation Tool')

    def test_test_case_tool(self):
        self.assertNotEqual(self.rtool, None)
        self.assertEqual(self.rtool.getId(), 'portal_relations')
        self.assertEqual(self.rtool.meta_type, 'Relation Tool')
        self.assert_(isinstance(self.rtool, RelationTool))

    def test_getSupportedGraphTypes(self):
        self.assertEquals(self.rtool.getSupportedGraphTypes(),
                          DEFAULT_GRAPH_TYPES)

    def test_listGraphIds(self):
        self.assertEqual(self.rtool.listGraphIds(), [])
        self.rtool.addGraph('iobtreegraph', 'IOBTree Graph')
        self.assertEqual(self.rtool.listGraphIds(), ['iobtreegraph'])

    def test_deleteAllGraphs(self):
        self.rtool.addGraph('iobtreegraph', 'IOBTree Graph')
        self.assertEqual(self.rtool.listGraphIds(), ['iobtreegraph'])
        self.rtool.deleteAllGraphs()
        self.assertEqual(self.rtool.listGraphIds(), [])

    def test_hasGraph(self):
        self.rtool.addGraph('iobtreegraph', 'IOBTree Graph')
        self.assertEqual(self.rtool.hasGraph('iobtreegraph'), True)
        self.assertEqual(self.rtool.hasGraph('iobtreegrapheuh'), False)

    def test_addGraph(self):
        self.assertEqual(self.rtool.listGraphIds(), [])
        self.rtool.addGraph('iobtreegraph', 'IOBTree Graph')
        self.assertEqual(self.rtool.listGraphIds(), ['iobtreegraph'])
        iobtreegraph = self.rtool.getGraph('iobtreegraph')
        self.assertEqual(iobtreegraph.getId(), 'iobtreegraph')
        self.assertEqual(iobtreegraph.meta_type, 'IOBTree Graph')

    def test_deleteGraph(self):
        self.assertEqual(self.rtool.listGraphIds(), [])
        self.rtool.addGraph('iobtreegraph', 'IOBTree Graph')
        self.assertEqual(self.rtool.listGraphIds(), ['iobtreegraph'])
        self.rtool.deleteGraph('iobtreegraph')
        self.assertEqual(self.rtool.listGraphIds(), [])

    def test_getGraph(self):
        self.rtool.addGraph('iobtreegraph', 'IOBTree Graph')
        iobtreegraph = self.rtool.getGraph('iobtreegraph')
        self.assertEqual(iobtreegraph.getId(), 'iobtreegraph')
        self.assertEqual(iobtreegraph.meta_type, 'IOBTree Graph')

        none_graph = self.rtool.getGraph('foo')
        self.assertEqual(none_graph, None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRelationTool))
    return suite
