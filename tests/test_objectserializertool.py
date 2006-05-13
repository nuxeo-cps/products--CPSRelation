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

import unittest

from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

from zope.interface.verify import verifyClass

from Products.CPSRelation.tests.CPSRelationTestCase import CPSRelationTestCase
from Products.CPSRelation.tests.test_redland import USE_REDLAND

from Products.CPSRelation.node import Resource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.node import Literal
from Products.CPSRelation.statement import Statement
from Products.CPSRelation.relationtool import RelationTool
from Products.CPSRelation.interfaces import IObjectSerializerTool
from Products.CPSRelation.objectserializertool import ObjectSerializerTool
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


class TestObjectSerializerTool(CPSRelationTestCase):

    def setUp(self):
        self.root = Folder('root')
        # set them for acquisition pirposes, needed in expressions tests
        self.root._setObject('portal_relations', RelationTool())
        self.root._setObject('portal_url', FakeUrlTool())
        self.root._setObject('portal_serializer', ObjectSerializerTool())

        self.stool = getattr(self.root, 'portal_serializer')

        # test serializer
        self.expr = """python:[
            Statement(Resource(getattr(object, 'id')),
                      PrefixedResource('exp', 'hasTitle'),
                      Literal(getattr(object, 'title'))),
            ]
        """
        ser = ObjectSerializer('serializer', self.expr)
        ser_id = self.stool._setObject('serializer', ser)
        self.serializer = getattr(self.stool, ser_id)

        self.bindings = {
            'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            'exp': "http://www.example.org/",
            }
        self.bindings_tuple = (
            'rdf http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'exp http://www.example.org/',
            )

        # test object
        kw = {
            'title': 'Fake Object',
            'number': 666,
            'reference': "azerty",
            }
        self.object = FakeObject('fake_object', **kw)

    def tearDown(self):
        del self.root
        del self.object
        del self.stool
        del self.serializer
        del self.bindings
        del self.bindings_tuple
        del self.expr

    def test_interface(self):
        verifyClass(IObjectSerializerTool, ObjectSerializerTool)

    def test_creation(self):
        stool = ObjectSerializerTool()
        self.assertEqual(stool.getId(), 'portal_serializer')
        self.assertEqual(stool.meta_type, 'Object Serializer Tool')

    def test_test_case_tool(self):
        self.assertNotEqual(self.stool, None)
        self.assertEqual(self.stool.getId(), 'portal_serializer')
        self.assertEqual(self.stool.meta_type, 'Object Serializer Tool')
        self.assert_(isinstance(self.stool, ObjectSerializerTool))

    def test_hasSerializer(self):
        self.assertEqual(self.stool.hasSerializer('serializer'),
                         True)
        self.assertEqual(self.stool.hasSerializer('serializereuh'),
                         False)

    def test_addSerializer(self):
        self.assertEqual(self.stool.hasSerializer('new_serializer'),
                         False)
        new_expr = """python:[
            Statement(Resource(getattr(object, 'id')),
                      PrefixedResource('exp', 'hasTitle'),
                      Literal('My title')),
            Statement(Resource(getattr(object, 'id')),
                      PrefixedResource('exp', 'isTruly'),
                      Literal(getattr(object, 'title'))),
            ]"""
        self.stool.addSerializer('new_serializer', new_expr)
        self.assertEqual(self.stool.hasSerializer('new_serializer'),
                         True)
        self.assertRaises(ValueError,
                          self.stool.addSerializer,
                          'new_serializer',
                          new_expr)
        new_ser = self.stool.getSerializer('new_serializer')
        self.assertEqual(new_ser.getId(), 'new_serializer')
        self.assertEqual(new_ser.serialization_expr, new_expr)

    def test_deleteSerializer(self):
        self.assertEqual(self.stool.hasSerializer('serializer'),
                         True)
        self.stool.deleteSerializer('serializer')
        self.assertEqual(self.stool.hasSerializer('serializer'),
                         False)

    def test_getSerializer(self):
        self.assertEqual(self.stool.getSerializer('serializer'),
                         self.serializer)
        self.assertRaises(AttributeError,
                          self.stool.getSerializer,
                          'serializereuh')

    def test_getSerializationStatements(self):
        expected_statements = [
            Statement(Resource('fake_object'),
                      PrefixedResource('exp', 'hasTitle'),
                      Literal('Fake Object')),
            ]
        statements = self.serializer.getSerializationStatements(
            self.object, 'serializer')
        self.assertEqual(statements, expected_statements)

        # test with other serializer
        new_expr = """python:[
            Statement(Resource(getattr(object, 'id')),
                      PrefixedResource('exp', 'hasTitle'),
                      Literal('My title')),
            Statement(Resource(getattr(object, 'id')),
                      PrefixedResource('exp', 'isTruly'),
                      Literal(getattr(object, 'title'))),
            ]"""
        self.stool.addSerializer('new_serializer', new_expr)
        expected_statements = [
            Statement(Resource('fake_object'),
                      PrefixedResource('exp', 'hasTitle'),
                      Literal('My title')),
            Statement(Resource('fake_object'),
                      PrefixedResource('exp', 'isTruly'),
                      Literal('Fake Object')),
            ]
        statements = self.serializer.getSerializationStatements(
            self.object, 'new_serializer')
        self.assertEqual(statements, expected_statements, keep_order=False)


    # XXX AT: theses tests require Redland
    if USE_REDLAND and 0:
        def test_serializeGraph(self):
            from Products.CPSRelation.redlandgraph import Model, Statement
            from Products.CPSRelation.redlandgraph import Storage
            from Products.CPSRelation.redlandgraph import Node, Uri, NS
            namespace = NS(self.namespace_bindings.get('exp'))
            statements = [
                (Node(Uri('fake_object')), namespace['hasTitle'], 'My title'),
                (Node(Uri('fake_object')), namespace['isTruly'], 'Fake Object'),
                ]
            options = "new='yes',hash-type='memory',dir='.'"
            storage = Storage(storage_name="hashes",
                              name='dummy',
                              options_string=options)
            rdf_graph = Model(storage)
            for item in statements:
                rdf_graph.append(Statement(item[0], item[1], item[2]))
            serialization = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:exp="http://www.example.org/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="fake_object">
    <exp:isTruly>Fake Object</exp:isTruly>
  </rdf:Description>
  <rdf:Description rdf:about="fake_object">
    <exp:hasTitle>My title</exp:hasTitle>
  </rdf:Description>
</rdf:RDF>
"""
            self.assertEqual(self.stool.serializeGraph(rdf_graph,
                                                       bindings=self.bindings),
                             serialization)

        def test_getSerializationFromSerializer(self):
            # XXX make real statements
            new_expr = """python:[
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.example.org/')['hasTitle'],
             'My title'),
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.otherexample.org/')['isTruly'],
             getattr(object, 'title')),
            ]"""
            self.serializer.manage_changeProperties(serialization_expr=new_expr,
                                                    bindings=self.bindings_tuple)
            expected = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:exp="http://www.example.org/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="fake_object">
    <exp:hasTitle>My title</exp:hasTitle>
  </rdf:Description>
  <rdf:Description rdf:about="fake_object">
    <ns0:isTruly xmlns:ns0="http://www.otherexample.org/">Fake Object</ns0:isTruly>
  </rdf:Description>
</rdf:RDF>
"""
            serialization = self.stool.getSerializationFromSerializer(self.object,
                                                                      'serializer')
            self.assertEqual(serialization, expected)

        def test_getSerializationFromStatements(self):
            from Products.CPSRelation.redlandgraph import Node, Uri, NS
            namespace = NS(self.bindings.get('exp'))
            statements = [
                (Node(Uri('fake_object')), namespace['hasTitle'], 'My title'),
                (Node(Uri('fake_object')), namespace['isTruly'], 'Fake Object'),
               ]
            expected = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:exp="http://www.example.org/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="fake_object">
    <exp:isTruly>Fake Object</exp:isTruly>
  </rdf:Description>
  <rdf:Description rdf:about="fake_object">
    <exp:hasTitle>My title</exp:hasTitle>
  </rdf:Description>
</rdf:RDF>
"""
            serialization = self.stool.getSerializationFromStatements(statements,
                                                    bindings=self.bindings)
            self.assertEqual(serialization, expected)

        def test_getSerializationFromGraph(self):
            from Products.CPSRelation.redlandgraph import Model, Statement
            from Products.CPSRelation.redlandgraph import Storage
            from Products.CPSRelation.redlandgraph import Node, Uri, NS
            namespace = NS(self.bindings.get('exp'))
            statements = [
                (Node(Uri('fake_object')), namespace['hasTitle'], 'My title'),
                (Node(Uri('fake_object')), namespace['isTruly'], 'Fake Object'),
               ]
            options = "new='yes',hash-type='memory',dir='.'"
            storage = Storage(storage_name="hashes",
                              name='dummy',
                              options_string=options)
            rdf_graph = Model(storage)
            for item in statements:
                rdf_graph.append(Statement(item[0], item[1], item[2]))
            expected = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:exp="http://www.example.org/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="fake_object">
    <exp:isTruly>Fake Object</exp:isTruly>
  </rdf:Description>
  <rdf:Description rdf:about="fake_object">
    <exp:hasTitle>My title</exp:hasTitle>
  </rdf:Description>
</rdf:RDF>
"""
            serialization = self.stool.getSerializationFromGraph(rdf_graph,
                                                    bindings=self.bindings)
            self.assertEqual(serialization, expected)

        def test_getMultipleSerialization(self):
            # XXX make real statements
            new_expr = """python:[
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.example.org/')['hasTitle'],
             'My title'),
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.example.org/')['isTruly'],
             getattr(object, 'title')),
            ]"""
            self.serializer.manage_changeProperties(serialization_expr=new_expr,
                                                    bindings=self.bindings_tuple)
            other_expr = """python:[
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.otherexample.org/')['hasNumber'],
             str(getattr(object, 'number'))),
            (Node(Uri(getattr(object, 'id'))),
             NS('http://www.otherexample.org/')['hasReference'],
             getattr(object, 'reference')),
            ]"""
            self.stool.addSerializer('new_serializer', other_expr)
            kw = {
                'title': 'Other Fake Object',
                'number': 689,
                'reference': "My reference",
                }
            other_object = FakeObject('other_fake_object', **kw)
            objects_info = [
                (self.object, 'serializer'),
                (other_object, 'new_serializer'),
                ]
            expected = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:exp="http://www.example.org/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="other_fake_object">
    <ns0:hasReference xmlns:ns0="http://www.otherexample.org/">My reference</ns0:hasReference>
  </rdf:Description>
  <rdf:Description rdf:about="other_fake_object">
    <ns0:hasNumber xmlns:ns0="http://www.otherexample.org/">689</ns0:hasNumber>
  </rdf:Description>
  <rdf:Description rdf:about="fake_object">
    <exp:isTruly>Fake Object</exp:isTruly>
  </rdf:Description>
  <rdf:Description rdf:about="fake_object">
    <exp:hasTitle>My title</exp:hasTitle>
  </rdf:Description>
</rdf:RDF>
"""
            serialization = self.stool.getMultipleSerialization(objects_info)
            self.assertEqual(serialization, expected)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestObjectSerializerTool))
    return suite

