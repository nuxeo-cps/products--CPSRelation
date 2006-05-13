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
#-------------------------------------------------------------------------------
"""Test IOBTree Graph
"""

import unittest

from zope.interface.verify import verifyClass

from Products.CPSRelation.interfaces import IGraph
from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.node import VersionHistoryResource
from Products.CPSRelation.statement import Statement
from Products.CPSRelation.iobtree.iobtreegraph import IOBTreeGraph

from Products.CPSRelation.tests.CPSRelationTestCase import CPSRelationTestCase

class IOBTreeGraphTestCase(CPSRelationTestCase):
    """CPSRelation test case using IOBtree relations"""

    def setUp(self):
        CPSRelationTestCase.setUp(self)
        self.graph = IOBTreeGraph('iobtreegraph')
        self.graph.addRelation('hasPart',
                               prefix='cps',
                               subject_prefix='docid',
                               object_prefix='docid')
        self.hasPart = self.graph.hasPart
        self.addTestRelations()

    def addTestRelations(self):
        statements = [
            Statement(IVersionHistoryResource(self.proxy1),
                      PrefixedResource('cps', 'hasPart'),
                      IVersionHistoryResource(self.proxy2)),
            ]
        self.graph.add(statements)
        self.test_relations = statements

    def tearDown(self):
        del self.graph


class TestIOBTreeGraph(IOBTreeGraphTestCase):

    def test_interface(self):
        verifyClass(IGraph, IOBTreeGraph)

    def test_creation(self):
        dummy = IOBTreeGraph('dummy')
        self.assertEqual(dummy.getId(), 'dummy')
        self.assertEqual(dummy.meta_type, 'IOBTree Graph')

    def test_test_case_graph(self):
        self.assertEqual(self.graph.getId(), 'iobtreegraph')
        self.assertEqual(self.graph.meta_type, 'IOBTree Graph')
        self.assert_(isinstance(self.graph, IOBTreeGraph))
        self.assertEqual(self.graph._getRelations(),
                         [self.hasPart])

    # api tests

    def test__getRelations(self):
        self.assertEqual(self.graph._getRelations(),
                         [self.hasPart])

    def test__getRelation(self):
        self.assertEqual(self.graph._getRelation('hasPart'),
                         self.hasPart)

    def test_listRelationIds(self):
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart'])

    def test_deleteAllRelations(self):
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart'])
        self.graph.deleteAllRelations()
        self.assertEqual(self.graph.listRelationIds(), [])

    def test_hasRelation(self):
        self.assertEqual(self.graph.hasRelation('hasPart'),
                         True)
        self.assertEqual(self.graph.hasRelation('dummy'),
                         False)

    def test_addRelation(self):
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart'])
        self.graph.addRelation('dummy',
                               prefix='prefix',
                               subject_prefix='subject_prefix',
                               object_prefix='object_prefix')
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart', 'dummy'])
        dummy = self.graph._getRelation('dummy')
        self.assertEqual(dummy.getId(), 'dummy')
        self.assertEqual(dummy.meta_type, 'IOBTree Relation')
        property_items = [
            ('prefix', 'prefix'),
            ('subject_prefix', 'subject_prefix'),
            ('object_prefix', 'object_prefix'),
            ]
        self.assertEqual(dummy.propertyItems(), property_items)

    def test_deleteRelation(self):
        self.assertEqual(self.graph.listRelationIds(),
                         ['hasPart'])
        self.graph.deleteRelation('hasPart')
        self.assertEqual(self.graph.listRelationIds(), [])


    def test__getIOBTreeRelation(self):
        predicate = PrefixedResource('cps', 'hasPart')
        self.assertEqual(self.graph._getIOBTreeRelation(predicate),
                         self.hasPart)
        predicate = PrefixedResource('cps', 'dummy')
        self.assertEqual(self.graph._getIOBTreeRelation(predicate),
                         None)


    def test__getIOBTreeStatementsStructure(self):
        # add another relation
        self.graph.addRelation('hasComment',
                               prefix='cps',
                               subject_prefix='docid',
                               object_prefix='docid')
        hasComment = self.graph._getRelation('hasComment')
        statements = [
            Statement(PrefixedResource('docid', '777'),
                      PrefixedResource('cps', 'hasPart'),
                      PrefixedResource('docid', '888')),
            Statement(PrefixedResource('docid', '777'),
                      PrefixedResource('cps', 'hasPart'),
                      PrefixedResource('docid', '666')),
            Statement(PrefixedResource('docid', '1245'),
                      PrefixedResource('cps', 'hasComment'),
                      PrefixedResource('docid', '666')),
            ]
        structure = {
            hasComment: [(PrefixedResource('docid', '1245'),
                          PrefixedResource('docid', '666'))],
            self.hasPart: [(PrefixedResource('docid', '777'),
                            PrefixedResource('docid', '888')),
                           (PrefixedResource('docid', '777'),
                            PrefixedResource('docid', '666'))],
            }
        self.assertEqual(self.graph._getIOBTreeStatementsStructure(statements),
                         structure)


    # interface api tests

    def test_add(self):
        statement = Statement(PrefixedResource('docid', '777'),
                              PrefixedResource('cps', 'hasPart'),
                              PrefixedResource('docid', '666'))
        self.assertEqual(statement in self.graph, False)
        self.graph.add([statement])
        self.assertEqual(statement in self.graph, True)


    def test_remove(self):
        statement = self.test_relations[0]
        self.assertEqual(statement in self.graph, True)
        self.graph.remove([statement])
        self.assertEqual(statement in self.graph, False)


    def test_getStatements(self):
        self.assertEqual(self.graph.getStatements(), self.test_relations,
                         keep_order=False)


    def test_getSubjects(self):
        subject = IVersionHistoryResource(self.proxy1)
        predicate = PrefixedResource('cps', 'hasPart')
        object = IVersionHistoryResource(self.proxy2)
        self.assertEqual(self.graph.getSubjects(predicate, object),
                         [subject])


    def test_getPredicates(self):
        subject = IVersionHistoryResource(self.proxy1)
        predicate = PrefixedResource('cps', 'hasPart')
        object = IVersionHistoryResource(self.proxy2)
        self.assertEqual(self.graph.getPredicates(subject, object),
                         [predicate])


    def test_getObjects(self):
        # additional statement for duplicates
        subject = IVersionHistoryResource(self.proxy1)
        predicate = PrefixedResource('cps', 'hasPart')
        statement = Statement(subject,
                              predicate,
                              PrefixedResource('docid', '777'))
        self.graph.add([statement])
        objects = [
            IVersionHistoryResource(self.proxy2),
            # translated by the graph thanks to the prefix
            VersionHistoryResource('777'),
            ]
        self.assertEqual(self.graph.getObjects(subject, predicate),
                         objects, keep_order=False)


    def test__contains__(self):
        statement = self.test_relations[0]
        self.assertEqual(statement in self.graph.getStatements(),
                         True)
        self.assertEqual(statement in self.graph, True)
        statement = Statement(PrefixedResource('docid', '12345'),
                              PrefixedResource('cps', 'hasPart'),
                              PrefixedResource('foo', 'bar'))
        self.assertEqual(statement in self.graph.getStatements(),
                         False)
        self.assertEqual(statement in self.graph, False)


    def test_clear(self):
        self.assertEqual(len(self.graph) > 0, True)
        self.graph.clear()
        self.assertEqual(len(self.graph), 0)


    def test__len__(self):
        self.assertEqual(len(self.graph), 1)


    def test_query(self):
        self.assertRaises(NotImplementedError,
                          self.graph.query,
                          'query :)',
                          'language')


    def test_read(self):
        input_source = self.getTestData('base.rdf')
        self.assertRaises(NotImplementedError,
                          self.graph.read,
                          input_source)


    def test_write(self):
        self.assertRaises(NotImplementedError,
                          self.graph.write)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIOBTreeGraph))
    return suite
