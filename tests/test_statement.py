#!/usr/bin/python
# Copyright (c) 2006 Nuxeo SAS <http://nuxeo.com>
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
"""Test Statement
"""

import unittest

from Products.CPSRelation.node import Resource
from Products.CPSRelation.node import Literal
from Products.CPSRelation.statement import Statement


class TestStatement(unittest.TestCase):

    def test_creation(self):
        st = Statement(Resource('c'), Resource('p'), Literal('s'))
        self.assertEqual(st.subject, Resource('c'))
        self.assertEqual(st.predicate, Resource('p'))
        self.assertEqual(st.object, Literal('s'))


    def test_creation_failing(self):
        # subject is not a resource nor blank
        self.assertRaises(ValueError,
                          Statement,
                          Literal('c'),
                          Resource('p'),
                          Literal('s'))

    def test__eq__(self):
        st = Statement(Resource('c'), Resource('p'), Literal('s'))
        same_st = Statement(Resource('c'), Resource('p'), Literal('s'))
        other_st = Statement(Resource('c'), Resource('p'), Literal('s4'))
        self.assertEqual(st, same_st)
        self.assertNotEqual(st, other_st)


    def test__nonzero__(self):
        st = Statement(Resource('c'), Resource('p'), Literal('s'))
        self.assertEqual(not not st, True)
        st = Statement(Resource('c'), Resource('p'), None)
        self.assertEqual(not not st, True)
        st = Statement(None, None, None)
        self.assertEqual(not not st, False)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestStatement))
    return suite

