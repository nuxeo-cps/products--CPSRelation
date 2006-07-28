# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors: - Julien Anguenot <ja@nuxeo.com>
#          - Anahide Tchertchian <at@nuxeo.com>
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
# $Id$
"""Tests for RelationManager
"""

import unittest

import transaction

from difflib import ndiff

from Products.CPSRelation.tests.test_redland import USE_REDLAND

from Products.CPSRelation.commithooks import RelationManager
from Products.CPSRelation.commithooks import get_relation_manager
from Products.CPSRelation.commithooks import del_relation_manager

from Products.CPSRelation.node import Resource
from Products.CPSRelation.node import Literal
from Products.CPSRelation.statement import Statement
from Products.CPSRelation.iobtree.iobtreegraph import IOBTreeGraph
if USE_REDLAND:
    from Products.CPSRelation.redland.redlandgraph import RedlandGraph


class FakeBeforeCommitSubscribersManager:
    def addSubscriber(self, hook, order):
        pass


# base test for other tests
class RelationManagerTest(unittest.TestCase):

    def setUp(self):
        self.graph = self._getGraph()
        self.other_graph = self._getOtherGraph()
        self.statements = self._getStatements()

    def tearDown(self):
        # make sure relation manager is deleted even if one test fails
        del_relation_manager()

    # test helpers

    def getDiff(self, first, second):
        msg = 'Tuples or lists are different:\n'
        try:
            # diff is more lisible presenting second item first
            msg += '\n'.join(list(ndiff(second, first)))
        except (TypeError, UnicodeDecodeError, AttributeError):
            # diff does work for given objects
            msg += '\n' + str(first) + ' != ' + str(second)
        return msg

    def assertEqual(self, first, second, msg=None, keep_order=False):
        """Modified version of assertEqual to deal with cases when order is not
        important in here so override it to sort lists/tuples.
        """
        if not keep_order:
            if isinstance(first, tuple):
                first_list = list(first)
                first_list.sort()
                first = tuple(first_list)
            elif isinstance(first, list):
                first.sort()
            if isinstance(second, tuple):
                second_list = list(second)
                second_list.sort()
                second = tuple(second_list)
            elif isinstance(second, list):
                second.sort()
        show_diff = False
        if (isinstance(first, (tuple, list))
            and isinstance(second, (tuple, list))
            and msg is None):
            show_diff = True
        try:
            return unittest.TestCase.assertEqual(self, first, second, msg)
        except AssertionError, err:
            if show_diff:
                err = self.getDiff(first, second)
            raise AssertionError(err)

    assertEquals = assertEqual

    # to subclass
    def _getGraph(self):
        raise NotImplementedError

    # to subclass
    def _getOtherGraph(self):
        raise NotImplementedError

    def _getStatements(self):
        statements = [
            Statement(Resource('12345'),
                      Resource('hasPart'),
                      Resource('54321')),
            Statement(Resource('78910'),
                      Resource('hasPart'),
                      Resource('10987')),
            Statement(Resource('666'),
                      Resource('hasPart'),
                      Resource('777')),
            ]
        return statements

    # tests

    def test_interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CPSCore.interfaces import IBeforeCommitSubscriber
        verifyClass(IBeforeCommitSubscriber, RelationManager)


    def test_add_synchronous(self):
        mgr = get_relation_manager()
        self.assertEquals(self.graph._isSynchronous(), True)
        self.assertEquals(len(self.graph), 0)
        # add
        self.graph.add(self.statements)
        self.assertEquals(self.graph.getStatements(),
                          self.statements)
        self.assertEquals(mgr._queue, {})
        # commit
        transaction.commit()
        self.assertEquals(self.graph.getStatements(),
                          self.statements)
        self.assertEquals(mgr._queue, {})


    def test_add_asynchronous(self):
        mgr = get_relation_manager()
        self.graph.synchronous = False
        self.assertEquals(self.graph._isSynchronous(), False)
        self.assertEquals(self.other_graph._isSynchronous(), True)
        self.assertEquals(len(self.graph), 0)
        self.assertEquals(len(self.other_graph), 0)
        # add
        self.graph.add(self.statements)
        self.other_graph.add(self.statements)
        self.assertEquals(len(self.graph), 0)
        self.assertEquals(self.other_graph.getStatements(),
                          self.statements)
        queue = {
            self.graph.getId(): {
                'graph': self.graph,
                'add': self.statements,
                'remove': [],
                },
            }
        self.assertEquals(mgr._queue, queue)
        # commit
        transaction.commit()
        self.assertEquals(self.graph.getStatements(),
                          self.statements)
        self.assertEquals(self.other_graph.getStatements(),
                          self.statements)
        self.assertEquals(mgr._queue, {})


    def test_remove_synchronous(self):
        mgr = get_relation_manager()
        self.assertEquals(self.graph._isSynchronous(), True)
        self.graph._add(self.statements)
        self.assertEquals(len(self.graph), 3)
        # remove
        self.graph.remove([self.statements[0]])
        self.assertEquals(self.graph.getStatements(),
                          self.statements[1:])
        self.assertEquals(mgr._queue, {})
        # commit
        transaction.commit()
        self.assertEquals(self.graph.getStatements(),
                          self.statements[1:])
        self.assertEquals(mgr._queue, {})


    def test_remove_asynchronous(self):
        mgr = get_relation_manager()
        self.graph.synchronous = False
        self.assertEquals(self.graph._isSynchronous(), False)
        self.assertEquals(self.other_graph._isSynchronous(), True)
        self.graph._add(self.statements)
        self.other_graph._add(self.statements)
        self.assertEquals(len(self.graph), 3)
        self.assertEquals(len(self.other_graph), 3)
        # remove
        self.graph.remove([self.statements[0]])
        self.other_graph.remove([self.statements[0]])
        self.assertEquals(self.graph.getStatements(),
                          self.statements)
        self.assertEquals(self.other_graph.getStatements(),
                          self.statements[1:])
        queue = {
            self.graph.getId(): {
                'graph': self.graph,
                'add': [],
                'remove': [self.statements[0]],
                },
            }
        self.assertEquals(mgr._queue, queue)
        # commit
        transaction.commit()
        self.assertEquals(self.graph.getStatements(),
                          self.statements[1:])
        self.assertEquals(self.other_graph.getStatements(),
                          self.statements[1:])
        self.assertEquals(mgr._queue, {})


    def test_complex_asynchronous(self):
        # add and remove within same transaction, using several asynchronous
        # graphs
        mgr = get_relation_manager()
        self.graph.synchronous = False
        self.other_graph.synchronous = False
        self.assertEquals(self.graph._isSynchronous(), False)
        self.assertEquals(self.other_graph._isSynchronous(), False)
        self.assertEquals(len(self.graph), 0)
        self.assertEquals(len(self.other_graph), 0)
        # addand remove
        self.graph.add(self.statements)
        self.graph.remove([self.statements[0]])
        self.other_graph.add(self.statements)
        self.other_graph.remove([self.statements[-1]])
        self.assertEquals(len(self.graph), 0)
        self.assertEquals(len(self.other_graph), 0)
        queue = {
            self.graph.getId(): {
                'graph': self.graph,
                'add': self.statements,
                'remove': [self.statements[0]],
                },
            self.other_graph.getId(): {
                'graph': self.other_graph,
                'add': self.statements,
                'remove': [self.statements[-1]],
                },
            }
        self.assertEquals(mgr._queue, queue)
        # commit
        transaction.commit()
        self.assertEquals(self.graph.getStatements(),
                          self.statements[1:])
        self.assertEquals(self.other_graph.getStatements(),
                          self.statements[:-1])
        self.assertEquals(mgr._queue, {})


class RelationManagerIOBTreeTest(RelationManagerTest):

    def _getGraph(self):
        graph = IOBTreeGraph('iobtree', synchronous=True)
        graph.addRelation('hasPart')
        return graph

    def _getOtherGraph(self):
        graph = IOBTreeGraph('other_iobtree', synchronous=True)
        graph.addRelation('hasPart')
        return graph


class RelationManagerRedlandTest(RelationManagerTest):

    def _getGraph(self):
        return RedlandGraph('redland', backend='memory',
                            synchronous=True)

    def _getOtherGraph(self):
        return RedlandGraph('other_redland', backend='memory',
                            synchronous=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RelationManagerIOBTreeTest))
    if USE_REDLAND:
        suite.addTest(unittest.makeSuite(RelationManagerRedlandTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
