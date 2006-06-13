# -*- coding: ISO-8859-15 -*-
#!/usr/bin/python
# Copyright (c) 2004-2006 Nuxeo SAS <http://nuxeo.com>
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
"""Test Redland Graph
"""

USE_REDLAND = 0

from logging import getLogger
logger = getLogger("CPSRelation.test_redland")

# XXX check that Redland is installed before importing
try:
    import RDF
except ImportError, err:
    if str(err) != 'No module named RDF':
        raise
    logger.warn("cannot test Redland features")
else:
    USE_REDLAND = 1
    # XXX if necessary, RDF has a debug mode:
    #RDF.debug(1)
    from Products.CPSRelation.redland.interfaces import IRedlandGraph
    from Products.CPSRelation.redland.redlandgraph import RedlandGraph

import os
import unittest

import zope.interface
import zope.component

from Products.CPSRelation.interfaces import IVersionResource
from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.interfaces import IRpathResource
from Products.CPSRelation.interfaces import IStatementResource
from Products.CPSRelation.statement import Statement
from Products.CPSRelation.node import Resource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.node import Literal
from Products.CPSRelation.node import Blank
from Products.CPSRelation.node import VersionResource
from Products.CPSRelation.node import VersionHistoryResource
from Products.CPSRelation.node import RpathResource

from Products.CPSRelation.tests.CPSRelationTestCase import CPSRelationTestCase

class RedlandGraphTestCase(CPSRelationTestCase):
    """CPSRelation test case using Redland RDF graphs"""

    def setUp(self):
        CPSRelationTestCase.setUp(self)
        self.namespace_bindings = (
            "dc http://purl.org/dc/elements/1.1/",
            "uuid http://cps-project.org/uuid/",
            "cps http://cps-project.org/node/",
            )
        self.graph = RedlandGraph('rdfgraph', backend='memory',
                                  namespace_bindings=self.namespace_bindings)
        self.addBaseRelations(self.graph)

    def tearDown(self):
        del self.namespace_bindings
        del self.graph


class TestRedlandGraph(RedlandGraphTestCase):

    def test_interface(self):
        zope.interface.verify.verifyClass(IRedlandGraph, RedlandGraph)


    def test_creation(self):
        bindings = (
            "dc http://purl.org/dc/elements/1.1/",
            )
        dummy = RedlandGraph('dummy', backend='memory',
                             namespace_bindings=bindings)
        self.assertEqual(dummy.getId(), 'dummy')
        self.assertEqual(dummy.meta_type, 'Redland Graph')
        self.assertEqual(dummy.namespace_bindings, bindings)


    def test_test_case_graph(self):
        self.assertEqual(self.graph.getId(), 'rdfgraph')
        self.assertEqual(self.graph.meta_type, 'Redland Graph')
        self.assert_(isinstance(self.graph, RedlandGraph))
        self.assertEqual(self.graph.getStatements(), self.base_relations,
                         keep_order=False)

    # api tests

    def test__getGraph(self):
        self.assert_(isinstance(self.graph._getGraph(), RDF.Model))


    def test_getNamespaceBindings(self):
        bindings_dict = {
            "dc": "http://purl.org/dc/elements/1.1/",
            "cps": "http://cps-project.org/node/",
            "uuid": "http://cps-project.org/uuid/",
            }
        self.assertEqual(self.graph.getNamespaceBindings(), bindings_dict)


    def test__getRedlandNode_basic(self):
        self.assertEqual(self.graph._getRedlandNode(None), None)

        resource = self.graph._getRedlandNode(Resource('http://example.org'))
        self.assertEqual(resource, RDF.Node(uri_string='http://example.org'))

        resource = self.graph._getRedlandNode(PrefixedResource('cps', 'toto'))
        self.assertEqual(resource, RDF.Node(uri_string='http://cps-project.org/node/toto'))

        resource = self.graph._getRedlandNode(PrefixedResource('shmurk', 'toto'))
        self.assertEqual(resource, RDF.Node(uri_string='shmurk:toto'))

        blank = self.graph._getRedlandNode(Blank('blank'))
        self.assertEqual(blank, RDF.Node(blank='blank'))

        lit = self.graph._getRedlandNode(Literal(u"Héhé"))
        # use utf-8 encoded value
        self.assertEqual(lit, RDF.Node(literal="H\xc3\xa9h\xc3\xa9"))

        # literal with language
        lit = self.graph._getRedlandNode(Literal("Haha", language="en"))
        # use utf-8 encoded value
        self.assertEqual(lit, RDF.Node(literal="Haha", language="en"))

        # typed literal
        lit = self.graph._getRedlandNode(Literal("Hoho",
                                                 type="http://example.org"))
        self.assertEqual(lit, RDF.Node(literal="Hoho",
                                       datatype=RDF.Uri("http://example.org")))

        # other typed literal
        lit = self.graph._getRedlandNode(Literal("2006-06-03 17:38:44",
                                                 type="date"))
        self.assertEqual(lit, RDF.Node(literal="2006-06-03 17:38:44",
                                       datatype=RDF.Uri("date")))


    def test__getRedlandNode_extended(self):
        version = self.graph._getRedlandNode(IVersionResource(self.proxy1))
        # version prefix is known by the graph
        version_uri_string = "http://cps-project.org/uuid/12345__0001"
        self.assertEqual(version, RDF.Node(uri_string=version_uri_string))

        vh = self.graph._getRedlandNode(IVersionHistoryResource(self.proxy1))
        self.assertEqual(vh, RDF.Node(uri_string="docid:12345"))

        rpath = self.graph._getRedlandNode(IRpathResource(self.proxy1))
        self.assertEqual(rpath, RDF.Node(uri_string="rpath:workspaces/proxy1"))


    def test__getCPSNode_basic(self):
        self.assertEqual(self.graph._getCPSNode(None), None)

        resource = self.graph._getCPSNode(RDF.Node(uri_string='http://example.org'))
        self.assertEqual(resource, Resource('http://example.org'))

        # use a namespace known by the graph: no changes, no factory for it
        uri_string = "http://purl.org/dc/elements/1.1/test"
        resource = self.graph._getCPSNode(RDF.Node(uri_string=uri_string))
        self.assertEqual(resource, PrefixedResource('dc', 'test'))

        blank = self.graph._getCPSNode(RDF.Node(blank='blank'))
        self.assertEqual(blank, Blank('blank'))

        # use utf-8 encoded value
        lit = self.graph._getCPSNode(RDF.Node(literal="H\xc3\xa9h\xc3\xa9"))
        self.assertEqual(lit, Literal(u"Héhé"))

        # literal with language
        lit = self.graph._getCPSNode(RDF.Node(literal="Haha", language="en"))
        # use utf-8 encoded value
        self.assertEqual(lit, Literal("Haha", language="en"))

        # typed literal
        lit = self.graph._getCPSNode(RDF.Node(literal="Hoho",
                                              datatype=RDF.Uri("http://example.org")))
        self.assertEqual(lit, Literal("Hoho",
                                      type="http://example.org"))

        # other typed literal
        lit = self.graph._getCPSNode(RDF.Node(literal="2006-06-03 17:38:44",
                                              datatype=RDF.Uri("date")))
        self.assertEqual(lit, Literal("2006-06-03 17:38:44",
                                      type="date"))


    def test__getCPSNode_extended(self):
        # version prefix is known by the graph, and resource registry too
        version_uri_string = "http://cps-project.org/uuid/12345__0001"
        version = self.graph._getCPSNode(RDF.Node(uri_string=version_uri_string))
        self.assertEqual(version, IVersionResource(self.proxy1))
        self.assertEqual(isinstance(version, Resource), True)
        # could be specific
        self.assertEqual(isinstance(version, VersionResource), True)

        # version prefix is known by the graph, but no special factory for it
        uri_string = "http://purl.org/dc/elements/1.1/test"
        resource = self.graph._getCPSNode(RDF.Node(uri_string=uri_string))
        self.assertEqual(resource, PrefixedResource('dc', 'test'))
        self.assertEqual(isinstance(resource, Resource), True)
        self.assertEqual(isinstance(resource, VersionResource), False)
        self.assertEqual(isinstance(resource, VersionHistoryResource), False)
        self.assertEqual(isinstance(resource, RpathResource), False)

        vh = self.graph._getCPSNode(RDF.Node(uri_string="docid:12345"))
        self.assertEqual(vh, IVersionHistoryResource(self.proxy1))
        self.assertEqual(isinstance(vh, Resource), True)
        # could not be more specific...
        self.assertEqual(isinstance(vh, VersionHistoryResource), False)

        rpath = self.graph._getCPSNode(RDF.Node(uri_string="rpath:workspaces/proxy1"))
        self.assertEqual(rpath, IRpathResource(self.proxy1))
        self.assertEqual(isinstance(vh, Resource), True)
        # could not be more specific...
        self.assertEqual(isinstance(vh, RpathResource), False)


    def test__getRedlandStatement(self):
        statement = Statement(None, None, None)
        rstatement = RDF.Statement(None, None, None)
        # XXX statements comparison with None node fails in Redland...
        #self.assertEqual(self.graph._getRedlandStatement(statement),
        #                 rstatement)
        statement = Statement(PrefixedResource('cps', 'cps'),
                              PrefixedResource('cps', 'title'),
                              Literal('CPS Project'))
        rstatement = RDF.Statement(RDF.Node(uri_string='http://cps-project.org/node/cps'),
                                   RDF.Node(uri_string='http://cps-project.org/node/title'),
                                   RDF.Node(literal='CPS Project'))
        self.assertEqual(self.graph._getRedlandStatement(statement),
                         rstatement)


    def test__getCPSStatement(self):
        statement = Statement(None, None, None)
        rstatement = RDF.Statement(None, None, None)
        self.assertEqual(self.graph._getCPSStatement(rstatement),
                         statement)
        statement = Statement(PrefixedResource('cps', 'cps'),
                              PrefixedResource('cps', 'title'),
                              Literal('CPS Project'))
        rstatement = RDF.Statement(RDF.Node(uri_string='http://cps-project.org/node/cps'),
                                   RDF.Node(uri_string='http://cps-project.org/node/title'),
                                   RDF.Node(literal='CPS Project'))
        self.assertEqual(self.graph._getCPSStatement(rstatement),
                         statement)

    # interface api tests

    def test_add(self):
        statement = Statement(Resource('http://example.org'),
                              PrefixedResource('cps', 'title'),
                              Literal('My example'))
        self.assertEqual(self.graph.hasStatement(statement), False)
        self.graph.add([statement])
        self.assertEqual(self.graph.hasStatement(statement), True)


    def test_remove(self):
        statement = Statement(PrefixedResource('cps', 'cps'),
                              PrefixedResource('cps', 'title'),
                              Literal('CPS Project'))
        self.assertEqual(self.graph.hasStatement(statement), True)
        self.graph.remove([statement])
        self.assertEqual(self.graph.hasStatement(statement), False)


    def test_getStatements(self):
        self.assertEqual(self.graph.getStatements(), self.base_relations,
                         keep_order=False)


    def test_getSubjects(self):
        subject = PrefixedResource('cps', 'cps')
        predicate = PrefixedResource('cps', 'title')
        literal = Literal('CPS Project')
        self.assertEqual(self.graph.getSubjects(predicate,
                                                literal),
                         [subject])
        self.assertEqual(self.graph.getSubjects(Resource('foo'),
                                                literal),
                         [])
        self.assertEqual(self.graph.getSubjects(predicate,
                                                Literal('bar')),
                         [])
        self.assertEqual(self.graph.getSubjects(Resource('foo'),
                                                Literal('bar')),
                         [])


    def test_getPredicates(self):
        subject = PrefixedResource('cps', 'cps')
        predicate = PrefixedResource('cps', 'title')
        literal = Literal('CPS Project')
        self.assertEqual(self.graph.getPredicates(subject,
                                                  literal),
                         [predicate])
        self.assertEqual(self.graph.getPredicates(Resource('foo'),
                                                  literal),
                         [])
        self.assertEqual(self.graph.getPredicates(subject,
                                                  Literal('bar')),
                         [])
        self.assertEqual(self.graph.getPredicates(Resource('foo'),
                                                  Literal('bar')),
                         [])


    def test_getObjects(self):
        subject = PrefixedResource('cps', 'cps')
        predicate = PrefixedResource('cps', 'title')
        statement = Statement(subject,
                              predicate,
                              Literal('CPS Project 4'))
        self.graph.add([statement])
        objects = [
            Literal('CPS Project'),
            Literal('CPS Project 4'),
            ]
        self.assertEqual(self.graph.getObjects(subject, predicate),
                         objects, keep_order=False)
        self.assertEqual(self.graph.getObjects(Resource('foo'),
                                               predicate),
                         [])
        self.assertEqual(self.graph.getObjects(subject,
                                               Resource('bar')),
                         [])
        self.assertEqual(self.graph.getObjects(Resource('foo'),
                                               Resource('bar')),
                         [])


    def test_hasStatement(self):
        statement = Statement(PrefixedResource('cps', 'cps'),
                              PrefixedResource('cps', 'title'),
                              Literal('CPS Project'))
        self.assertEqual(statement in self.graph.getStatements(),
                         True)
        self.assertEqual(self.graph.hasStatement(statement), True)
        # None value
        statement = Statement(PrefixedResource('cps', 'cps'),
                              PrefixedResource('cps', 'title'),
                              None)
        self.assertEqual(self.graph.hasStatement(statement), True)
        statement = Statement(PrefixedResource('cps', 'cps3'),
                              PrefixedResource('cps', 'title'),
                              Literal('CPS Project'))
        self.assertEqual(statement in self.graph.getStatements(),
                         False)
        self.assertEqual(self.graph.hasStatement(statement), False)
        # graph is not empty
        statement = Statement(None, None, None)
        self.assertEqual(self.graph.hasStatement(statement), True)
        self.graph.clear()
        self.assertEqual(self.graph.hasStatement(statement), False)


    def test_hasResource(self):
        self.assertEqual(self.graph.hasResource(PrefixedResource('cps', 'cps')),
                         True)
        self.assertEqual(self.graph.hasResource(PrefixedResource('cps', 'cps3')),
                         False)


    def test_clear(self):
        self.assertEqual(len(self.graph) > 0, True)
        self.graph.clear()
        self.assertEqual(len(self.graph), 0)


    def test__len__(self):
        self.assertEqual(len(self.graph), 3)


    # test queries, this is mainly to show query examples

    def test_query_simple(self):
        statement = Statement(Resource('http://example.org/toto'),
                              PrefixedResource('cps', 'exp'),
                              Literal('CPS Project'))
        self.graph.add([statement])


        query = """
PREFIX cps: <%s>
SELECT ?subj, ?obj
WHERE {
  ?subj cps:title ?obj .
  FILTER REGEX(?obj, "^CPS.*")
}
"""%(self.graph.getNamespaceBindings().get('cps'),)

        result = self.graph.query(query, language='sparql')
        self.assertEqual(result.count, 1)
        self.assertEqual(result.variable_names, ['subj', 'obj'],
                         keep_order=False)
        expected = [
            {'subj': PrefixedResource('cps', 'cps'),
             'obj': Literal('CPS Project'),
             },
            ]
        self.assertEqual(result.results, expected)

        # do not filter on predicate
        query = """
PREFIX cps: <%s>
SELECT ?subj, ?pred, ?obj
WHERE {
  ?subj ?pred ?obj .
  FILTER REGEX(?obj, "^CPS.*")
}
"""%(self.graph.getNamespaceBindings().get('cps'),)

        result = self.graph.query(query, language='sparql')
        self.assertEqual(result.count, 2)
        self.assertEqual(result.variable_names, ['subj', 'pred', 'obj'],
                         keep_order=False)
        expected = [
            {'subj': PrefixedResource('cps', 'cps'),
             'pred': PrefixedResource('cps', 'title'),
             'obj': Literal('CPS Project'),
             },
            {'subj': Resource('http://example.org/toto'),
             'pred': PrefixedResource('cps', 'exp'),
             'obj': Literal('CPS Project'),
             },
            ]
        self.assertEqual(result.results, expected, keep_order=False)


    def test_query_order(self):
        namespace_bindings = (
            "cps http://cps-project.org/node/",
            )
        test_graph = RedlandGraph('dummy', backend='memory',
                                  namespace_bindings=namespace_bindings)
        # root
        #   section1
        #   my section 2
        #   section3
        hasPart = PrefixedResource('cps', 'hasPart')
        hasOrder = PrefixedResource('cps', 'hasOrder')
        statements = [
            Statement(Resource('root'), hasPart, Resource('section1')),
            Statement(Resource('section1'), hasOrder, Literal('1')),
            Statement(Resource('root'), hasPart, Resource('my section 2')),
            Statement(Resource('my section 2'), hasOrder, Literal('2')),
            Statement(Resource('root'), hasPart, Resource('section3')),
            Statement(Resource('section3'), hasOrder, Literal('3')),
            ]
        test_graph.add(statements)
        query = """
PREFIX cps: <%s>
SELECT ?obj
WHERE {
  ?subj cps:hasPart ?obj
  ?obj cps:hasOrder ?order
}
ORDER BY ?order
"""% (test_graph.getNamespaceBindings().get('cps'),)

        result = test_graph.query(query, language='sparql')
        self.assertEqual(result.count, 3)
        self.assertEqual(result.variable_names, ['obj'])
        expected = [
            {'obj': Resource('section1'),},
            {'obj': Resource('my section 2'),},
            {'obj': Resource('section3'),},
            ]
        self.assertEqual(result.results, expected)


    def test_query_node(self):
        base_uri = self.graph.getNamespaceBindings().get('cps')
        query = """
PREFIX cps: <%s>
SELECT ?title
WHERE {
  <cps> cps:title ?title .
}
"""%(base_uri,)

        result = self.graph.query(query, 'sparql',
                                  base_uri=base_uri)
        self.assertEqual(result.variable_names, ['title'])
        self.assertEqual(result.count, 1)
        self.assertEqual(result.results,
                         [{'title': Literal('CPS Project'),},])


    def test_query_literal(self):
        statement = Statement(Resource('http://example.org/toto'),
                              PrefixedResource('cps', 'title'),
                              Literal('Example'))
        self.graph.add([statement])
        query = """
PREFIX cps: <%s>
SELECT ?subj
WHERE {
  ?subj cps:title "Example"
}
"""%(self.graph.getNamespaceBindings().get('cps'),)

        result = self.graph.query(query, 'sparql',
                                  base_uri="http://example.org")
        self.assertEqual(result.variable_names, ['subj'])
        self.assertEqual(result.count, 1)
        self.assertEqual(result.results,
                         [{'subj': Resource('http://example.org/toto'),},])


    def test_query_literal_language(self):
        statement = Statement(Resource('http://example.org/toto'),
                              PrefixedResource('cps', 'title'),
                              Literal('Example', language="en"))
        self.graph.add([statement])
        query = """
PREFIX cps: <%s>
SELECT ?subj
WHERE {
  ?subj cps:title "Example"@en
}
"""%(self.graph.getNamespaceBindings().get('cps'),)

        result = self.graph.query(query, 'sparql',
                                  base_uri="http://example.org")
        self.assertEqual(result.variable_names, ['subj'])
        self.assertEqual(result.count, 1)
        self.assertEqual(result.results,
                         [{'subj': Resource('http://example.org/toto'),},])



    def test_query_literal_datatype(self):
        statement = Statement(Resource('http://example.org/toto'),
                              PrefixedResource('cps', 'title'),
                              Literal('Example',
                                      type="http://example.org/string/"))
        self.graph.add([statement])
        query = """
PREFIX cps: <%s>
SELECT ?subj
WHERE {
  ?subj cps:title "Example"^^<http://example.org/string/>
}
"""%(self.graph.getNamespaceBindings().get('cps'),)

        result = self.graph.query(query, 'sparql',
                                  base_uri="http://example.org")
        self.assertEqual(result.variable_names, ['subj'])
        self.assertEqual(result.count, 1)
        self.assertEqual(result.results,
                         [{'subj': Resource('http://example.org/toto'),},])


    def test_query_negative(self):
        # test query meaning "all nodes that dont have that other relation"
        graph = RedlandGraph('dummy', backend='memory',
                             namespace_bindings=self.namespace_bindings)
        pred_dum = PrefixedResource('cps', 'dummy')
        lit = Literal('dummy')
        statements = [
            Statement(PrefixedResource('cps', 'cps'),
                      PrefixedResource('cps', 'title'),
                      Literal("My great title")),
            Statement(PrefixedResource('cps', 'cps'),
                      PrefixedResource('cps', 'dummy'),
                      Literal("Dummy")),
            Statement(PrefixedResource('cps', 'cps4'),
                      PrefixedResource('cps', 'dummy'),
                      Literal("Other dummy")),
            ]
        self.graph.add(statements)

        # XXX the dot before FILTER is needed, otherwise Redland crashes...
        query = """
        PREFIX cps: <%s>
SELECT ?subj
WHERE {
  ?subj cps:dummy ?dum .
  OPTIONAL {?subj cps:title ?obj} .
  FILTER (!BOUND(?obj))
}
"""%(self.graph.getNamespaceBindings().get('cps'),)

        result = self.graph.query(query, 'sparql')
        expected = [
            {'subj': PrefixedResource('cps', 'cps4')},
            ]
        self.assertEqual(result.results, expected)


    def test_read(self):
        test_graph = RedlandGraph('dummy', backend='memory')

        self.assertEqual(len(test_graph), 0)

        input_source = self.getTestData('base.rdf')
        test_graph.read(input_source)

        # XXX cannot compare to base relations, blank node id is lost...
        #self.assertEqual(test_graph.getStatements(),
        #                 self.base_relations, keep_order=False)
        self.assertEqual(len(test_graph), 3)


    def test_write(self):
        serialization = self.graph.write()
        expected_serialization = self.getTestData('base.rdf')
        self.assertEquals(serialization, expected_serialization)

    def test_write_newline(self):
        # this is a test for a Redland bug that does not convert new lines
        # correctly in some versions
        graph = RedlandGraph('rdfgraph_nl', backend='memory',
                             namespace_bindings=self.namespace_bindings)
        statements = [
            Statement(Resource("1"),
                      PrefixedResource("cps", "dummy"),
                      Literal('hello\r\nhowdy?')),
            Statement(Resource("2"),
                      PrefixedResource("cps", "dummy"),
                      Literal('hello\nagain')),
            ]
        graph.add(statements)
        expected = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:cps="http://cps-project.org/node/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:uuid="http://cps-project.org/uuid/">
  <rdf:Description rdf:about="1">
    <cps:dummy>hello&#xD;
howdy?</cps:dummy>
  </rdf:Description>
  <rdf:Description rdf:about="2">
    <cps:dummy>hello
again</cps:dummy>
  </rdf:Description>
</rdf:RDF>
"""
        self.assertEquals(graph.write(), expected)


    def test_StatementResource(self):
        statement = Statement(IVersionHistoryResource(self.proxy1),
                              PrefixedResource('cps', 'hasTitle'),
                              Literal(u"Héhéhé"))
        resource = zope.component.queryMultiAdapter(
            (statement, self.graph),
            IStatementResource)
        self.assertEqual(resource.uri,
                         "statement:56d6d923420f177924e1873e787374fd4617b054")
        self.assertEqual(resource.prefix, "statement")
        self.assertEqual(resource.localname,
                         "56d6d923420f177924e1873e787374fd4617b054")

        # test resource is the same even if given statement is different
        other_statement = Statement(PrefixedResource('docid', '12345'),
                                    PrefixedResource('cps', 'hasTitle'),
                                    Literal(u"Héhéhé"))
        other_resource = zope.component.queryMultiAdapter(
            (other_statement, self.graph),
            IStatementResource)
        self.assertEqual(resource, other_resource)


def test_suite():
    suite = unittest.TestSuite()
    if USE_REDLAND:
        suite.addTest(unittest.makeSuite(TestRedlandGraph))
        # add other test cases here
    return suite
