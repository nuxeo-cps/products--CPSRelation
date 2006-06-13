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
"""Tests for Object Serializer
"""

import unittest

from zope.interface.verify import verifyClass

from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.Expression import Expression

from Products.CPSRelation.tests.CPSRelationTestCase import CPSRelationTestCase

from Products.CPSRelation.node import Resource
from Products.CPSRelation.node import Literal
from Products.CPSRelation.statement import Statement
from Products.CPSRelation.relationtool import RelationTool
from Products.CPSRelation.interfaces import IObjectSerializer
from Products.CPSRelation.objectserializer import ObjectSerializer


class FakeObject(SimpleItem):

    def __init__(self, id, **kw):
        self.id = id
        # kws are set as attributes
        for k, v in kw.items():
            setattr(self, k, v)

class FakeUrlTool(Folder):
    id = 'portal_url'

    def getPortalObject(self):
        return FakeObject(id="portal")

class FakeSerializerTool(Folder):
    id = 'portal_serializer'


class TestObjectSerializer(CPSRelationTestCase):

    def setUp(self):
        # test object and environment
        root = Folder('root')
        self.root = root
        kw = {
            'title': 'Fake Object',
            'number': 666,
            'reference': "azerty",
            }
        # needed for expression tests
        ob_id = root._setObject('fake_object', FakeObject('fake_object', **kw))
        self.object = getattr(root, ob_id)
        root._setObject('portal_relations', RelationTool())
        root._setObject('portal_url', FakeUrlTool())
        root._setObject('portal_serializer', FakeSerializerTool())

        self.expr = """python:[Statement(Resource(getattr(object, 'id')),
                                         Resource('hasTitle'),
                                         Literal(getattr(object, 'title')))]"""
        ser = ObjectSerializer('serializer', self.expr)
        ser_id = root._setObject('serializer', ser)
        self.serializer = getattr(root, ser_id)

    def tearDown(self):
        del self.root
        del self.object
        del self.serializer
        del self.expr

    def test_interface(self):
        verifyClass(IObjectSerializer, ObjectSerializer)

    def test_creation_edition(self):
        expr = """python:[Statement(Resource(getattr(object, 'id')),
                                    PrefixedResource('cps', 'hasTitle'),
                                    Literal(getattr(object, 'title')))]"""
        serializer = ObjectSerializer('dummy', expr)
        self.assertEqual(serializer.getId(), 'dummy')
        self.assertEqual(serializer.meta_type, 'Object Serializer')
        self.assertEqual(serializer.serialization_expr, expr)
        new_expr = """python:[Statement(Resource(getattr(object, 'id')),
                                        PrefixedResource('cps', 'hasTitle'),
                                        Literal('My title'))]"""
        serializer.manage_changeProperties(serialization_expr=new_expr)
        self.assertEqual(serializer.serialization_expr, new_expr)
        # incorrect expression, PropertiesPostProcessor will throw an error
        inc_expr = """python:[Statement(Resource(getattr(object, 'id')),
                                        PrefixedResource('cps', 'hasTitle'),
                                        Literal('My title')"""
        try:
            # Zope 2.10
            from zope.tales.tales import CompilerError
        except ImportError:
            # BBB for Zope 2.9
            from Products.PageTemplates.TALES import CompilerError
        self.assertRaises(CompilerError,
                          serializer.manage_changeProperties,
                          serialization_expr=inc_expr)
        # incorrect creation : same
        self.assertRaises(CompilerError,
                          ObjectSerializer,
                          'dummy',
                          inc_expr)

    def test_test_case_serializer(self):
        self.assertNotEqual(self.serializer, None)
        self.assertEqual(self.serializer.getId(), 'serializer')
        self.assertEqual(self.serializer.meta_type, 'Object Serializer')
        self.assert_(isinstance(self.serializer, ObjectSerializer))
        self.assertEqual(self.serializer.serialization_expr, self.expr)

    def test__createExpressionContext(self):
        context = self.serializer._createExpressionContext(self.object)
        # test namespace elements
        expr_c = Expression("python:object")
        self.assertEqual(expr_c(context), self.object)
        expr_c = Expression("python:container")
        self.assertEqual(expr_c(context), self.root)
        expr_c = Expression("python:user")
        self.assertEqual(expr_c(context).getUserName(), 'Anonymous User')
        expr_c = Expression("python:portal")
        self.assert_(isinstance(expr_c(context), FakeObject))
        self.assertEqual(expr_c(context).getId(), 'portal')
        expr_c = Expression("python:portal_relations")
        self.assert_(isinstance(expr_c(context), RelationTool))
        self.assertEqual(expr_c(context).getId(), 'portal_relations')
        expr_c = Expression("python:portal_serializer")
        self.assert_(isinstance(expr_c(context), FakeSerializerTool))
        self.assertEqual(expr_c(context).getId(), 'portal_serializer')
        # etc...

    def test_getStatements(self):
        statements = [Statement(Resource('fake_object'),
                                Resource('hasTitle'),
                                Literal('Fake Object'))]
        self.assertEqual(self.serializer.getStatements(self.object),
                         statements)
        new_expr = """python:[
            Statement(Resource(getattr(object, 'id')),
                      Resource('hasTitle'),
                      Literal('My title')),
            Statement(Resource(getattr(object, 'id')),
                      Resource('isTruly'),
                      Literal(getattr(object, 'title'))),
            ]"""
        self.serializer.manage_changeProperties(serialization_expr=new_expr)
        statements = [
            Statement(Resource('fake_object'),
                      Resource('hasTitle'),
                      Literal('My title')),
            Statement(Resource('fake_object'),
                      Resource('isTruly'),
                      Literal('Fake Object')),
            ]
        self.assertEqual(self.serializer.getStatements(self.object),
                         statements)

    def test_getNamespaceBindings(self):
        self.assertEqual(self.serializer.getNamespaceBindings(), {})
        bindings_tuple = (
            'rdf http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'exp http://www.example.org/',
            )
        self.serializer.manage_changeProperties(
            namespace_bindings=bindings_tuple)
        bindings_dict = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'exp': 'http://www.example.org/',
            }
        self.assertEqual(self.serializer.getNamespaceBindings(),
                         bindings_dict)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestObjectSerializer))
    return suite
