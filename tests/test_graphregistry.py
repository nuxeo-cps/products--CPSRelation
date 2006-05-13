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
"""Graph registry tests
"""

import unittest

from Products.CPSRelation.tests.CPSRelationTestCase import CPSRelationTestCase
from Products.CPSRelation.tests.test_redland import USE_REDLAND

from Products.CPSRelation.graphregistry import GraphRegistry
from Products.CPSRelation.iobtree.iobtreegraph import IOBTreeGraph
if USE_REDLAND:
    from Products.CPSRelation.redland.redlandgraph import RedlandGraph

# default graph types registered at product setup. To be modified when adding
# new graph types
DEFAULT_GRAPH_TYPES = [
    IOBTreeGraph.meta_type,
    ]
if USE_REDLAND:
    DEFAULT_GRAPH_TYPES.append(RedlandGraph.meta_type)

class DummyGraph:
    meta_type = 'Dummy Graph'

class TestGraphRegistry(CPSRelationTestCase):

    def setUp(self):
        self.save_graph_classes = GraphRegistry._graph_classes.copy()

    def tearDown(self):
        GraphRegistry._graph_classes = self.save_graph_classes

    def test_listGraphTypes(self):
        graph_types = DEFAULT_GRAPH_TYPES
        self.assertEquals(GraphRegistry.listGraphTypes(), graph_types,
                          keep_order=False)

    def test_register(self):
        GraphRegistry.register(DummyGraph)
        graph_types = DEFAULT_GRAPH_TYPES + ['Dummy Graph']
        self.assertEquals(GraphRegistry.listGraphTypes(), graph_types,
                          keep_order=False)

    def test_makeIOBTreeGraph(self):
        graph = GraphRegistry.makeGraph(IOBTreeGraph.meta_type,
                                        'test_iobtreegraph')
        self.assertEquals(graph.meta_type, IOBTreeGraph.meta_type)
        self.assertEquals(graph.getId(), 'test_iobtreegraph')
        self.assert_(isinstance(graph, IOBTreeGraph))

    def test_makeRedlandGraph(self):
        if not USE_REDLAND:
            return
        graph = GraphRegistry.makeGraph(RedlandGraph.meta_type,
                                        'test_redlandgraph')
        self.assertEquals(graph.meta_type, RedlandGraph.meta_type)
        self.assertEquals(graph.getId(), 'test_redlandgraph')
        self.assert_(isinstance(graph, RedlandGraph))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGraphRegistry))
    return suite

