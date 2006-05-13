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
"""Test IOBTree Relation
"""

import unittest

from zope.interface.verify import verifyClass

# register nodes
from Products.CPSRelation import node

from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.node import Resource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.node import VersionResource
from Products.CPSRelation.node import RpathResource
from Products.CPSRelation.statement import Statement

from Products.CPSRelation.iobtree.interfaces import IIOBTreeRelation
from Products.CPSRelation.iobtree.iobtreerelation import IOBTreeRelation

from Products.CPSRelation.tests.CPSRelationTestCase import CPSRelationTestCase


class TestIOBtreeRelation(CPSRelationTestCase):
    """Test IOBTree Relation"""

    def setUp(self):
        CPSRelationTestCase.setUp(self)
        # add test relations
        self.hasPart = IOBTreeRelation('hasPart',
                                       prefix='cps',
                                       subject_prefix='docid',
                                       object_prefix='docid')

    def addTestRelations(self):
        self.hasPart.add([(IVersionHistoryResource(self.proxy1),
                           IVersionHistoryResource(self.proxy2))])


    def test_interface(self):
        verifyClass(IIOBTreeRelation, IOBTreeRelation)

    def test_creation(self):
        dummy = IOBTreeRelation('dummy',
                                prefix='prefix',
                                subject_prefix='subject_prefix',
                                object_prefix='object_prefix')
        self.assertEqual(dummy.getId(), 'dummy')
        self.assertEqual(dummy.meta_type, 'IOBTree Relation')
        property_items = [
            ('prefix', 'prefix'),
            ('subject_prefix', 'subject_prefix'),
            ('object_prefix', 'object_prefix'),
            ]
        self.assertEqual(dummy.propertyItems(), property_items)


    def test_test_case_relations(self):
        self.assertEqual(self.hasPart.getId(), 'hasPart')
        self.assertEqual(self.hasPart.meta_type, 'IOBTree Relation')
        property_items = [
            ('prefix', 'cps'),
            ('subject_prefix', 'docid'),
            ('object_prefix', 'docid'),
            ]
        self.assertEqual(self.hasPart.propertyItems(), property_items)


    def test__getIntegerIdentifier(self):
        resource = IVersionHistoryResource(self.proxy1)
        self.assertEqual(self.hasPart._getIntegerIdentifier(resource,
                                                            prefix='docid'),
                         12345)
        self.assertRaises(ValueError,
                          self.hasPart._getIntegerIdentifier,
                          Resource('hihihi'))


    def test__getCPSNode(self):
        self.assertEqual(self.hasPart._getCPSNode('12345', prefix='docid'),
                         IVersionHistoryResource(self.proxy1))
        self.assertEqual(self.hasPart._getCPSNode('12345__0001', prefix='uuid'),
                         VersionResource('12345__0001'))
        self.assertEqual(self.hasPart._getCPSNode('12345', prefix='rpath'),
                         RpathResource('12345'))
        self.assertEqual(self.hasPart._getCPSNode('12345', prefix='docideuh'),
                         PrefixedResource('docideuh', '12345'))
        self.assertEqual(self.hasPart._getCPSNode('12345'),
                         Resource('12345'))


    def test__getCPSRelation(self):
        self.assertEqual(self.hasPart._getCPSRelation(),
                         PrefixedResource('cps', 'hasPart'))
        self.hasPart.prefix = 'rpath'
        self.assertEqual(self.hasPart._getCPSRelation(),
                         RpathResource('hasPart'))
        self.hasPart.prefix = ''
        self.assertEqual(self.hasPart._getCPSRelation(),
                         Resource('hasPart'))


    def test__add(self):
        self.assertEqual(list(self.hasPart.relations.items()), [])
        self.assertEqual(list(self.hasPart.inverse_relations.items()), [])
        self.hasPart._add(1, 2)
        self.assertEqual(list(self.hasPart.relations.items()),
                         [(1, [2])])
        self.assertEqual(list(self.hasPart.inverse_relations.items()), [])
        self.hasPart._add(2, 1, inverse=True)
        self.assertEqual(list(self.hasPart.relations.items()),
                         [(1, [2])])
        self.assertEqual(list(self.hasPart.inverse_relations.items()),
                         [(2, [1])])


    def test__remove(self):
        self.assertEqual(list(self.hasPart.relations.items()), [])
        self.assertEqual(list(self.hasPart.inverse_relations.items()), [])
        self.hasPart._add(1, 2)
        self.hasPart._add(2, 1, inverse=True)
        self.assertEqual(list(self.hasPart.relations.items()),
                         [(1, [2])])
        self.assertEqual(list(self.hasPart.inverse_relations.items()),
                         [(2, [1])])
        self.hasPart._remove(1, 2)
        self.assertEqual(list(self.hasPart.relations.items()), [])
        self.assertEqual(list(self.hasPart.inverse_relations.items()),
                         [(2, [1])])
        self.hasPart._remove(2, 1, inverse=True)
        self.assertEqual(list(self.hasPart.relations.items()), [])
        self.assertEqual(list(self.hasPart.inverse_relations.items()), [])


    def test_add(self):
        self.assertEqual(list(self.hasPart.relations.items()), [])
        self.assertEqual(list(self.hasPart.inverse_relations.items()), [])
        self.addTestRelations()
        self.assertEqual(list(self.hasPart.relations.items()),
                         [(12345, [666])])
        self.assertEqual(list(self.hasPart.inverse_relations.items()),
                         [(666, [12345])])


    def test_remove(self):
        self.addTestRelations()
        self.assertEqual(list(self.hasPart.relations.items()),
                         [(12345, [666])])
        self.assertEqual(list(self.hasPart.inverse_relations.items()),
                         [(666, [12345])])
        self.hasPart.remove([(IVersionHistoryResource(self.proxy1),
                              IVersionHistoryResource(self.proxy2))])
        self.assertEqual(list(self.hasPart.relations.items()), [])
        self.assertEqual(list(self.hasPart.inverse_relations.items()), [])


    def test_getObjects(self):
        self.addTestRelations()
        targets = self.hasPart.getObjects(IVersionHistoryResource(self.proxy1))
        self.assertEqual(targets, [IVersionHistoryResource(self.proxy2)])
        targets = self.hasPart.getObjects(IVersionHistoryResource(self.proxy2))
        self.assertEqual(targets, [])


    def test_getSubjects(self):
        self.addTestRelations()
        sources = self.hasPart.getSubjects(IVersionHistoryResource(self.proxy2))
        self.assertEqual(sources, [IVersionHistoryResource(self.proxy1)])
        sources = self.hasPart.getSubjects(IVersionHistoryResource(self.proxy1))
        self.assertEqual(sources, [])


    def test_getStatements(self):
        subject = IVersionHistoryResource(self.proxy1)
        predicate = PrefixedResource('cps', 'hasPart')
        object = IVersionHistoryResource(self.proxy2)
        statement = Statement(subject, predicate, object)
        self.assertEqual(self.hasPart.getStatements(), [])
        self.assertEqual(self.hasPart.getStatements(subject=subject,
                                                    object=object),
                         [])

        # add tests relations
        self.addTestRelations()
        self.hasPart.add([(subject, subject)])

        statements = [
            statement,
            Statement(subject, predicate, subject),
            ]
        self.assertEqual(self.hasPart.getStatements(), statements)

        self.assertEqual(self.hasPart.getStatements(subject=subject,
                                                    object=object),
                         [statement])
        self.assertEqual(self.hasPart.getStatements(subject=object,
                                                    object=subject),
                         [])
        # wild cards
        self.assertEqual(self.hasPart.getStatements(subject=None,
                                                    object=None),
                         statements)
        self.assertEqual(self.hasPart.getStatements(subject=subject,
                                                    object=None),
                         statements)
        self.assertEqual(self.hasPart.getStatements(subject=None,
                                                    object=object),
                         [statement])


    def test_hasTuple(self):
        subject = IVersionHistoryResource(self.proxy1)
        object = IVersionHistoryResource(self.proxy2)

        self.assertEqual(self.hasPart.hasTuple(), False)
        self.assertEqual(self.hasPart.hasTuple(subject=subject,
                                               object=object),
                         False)

        self.addTestRelations()
        self.assertEqual(self.hasPart.hasTuple(), True)
        self.assertEqual(self.hasPart.hasTuple(subject=subject,
                                               object=object),
                         True)
        self.assertEqual(self.hasPart.hasTuple(subject=subject,
                                               object=None),
                         True)
        self.assertEqual(self.hasPart.hasTuple(subject=None,
                                               object=object),
                         True)
        self.assertEqual(self.hasPart.hasTuple(subject=object,
                                               object=subject),
                         False)
        self.assertEqual(self.hasPart.hasTuple(subject=None,
                                               object=subject),
                         False)
        self.assertEqual(self.hasPart.hasTuple(subject=object,
                                               object=None),
                         False)


    def test_clear(self):
        self.assertEqual(len(self.hasPart), 0)
        self.addTestRelations()
        self.assertEqual(len(self.hasPart), 1)
        self.hasPart.clear()
        self.assertEqual(len(self.hasPart), 0)


    def test___len__(self):
        self.assertEqual(len(self.hasPart), 0)
        self.addTestRelations()
        self.assertEqual(len(self.hasPart), 1)
        subject = IVersionHistoryResource(self.proxy1)
        self.hasPart.add([(subject, subject)])
        self.assertEqual(len(self.hasPart), 2)
        object = IVersionHistoryResource(self.proxy2)
        self.hasPart.add([(object, object)])
        self.assertEqual(len(self.hasPart), 3)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIOBtreeRelation))
    return suite
