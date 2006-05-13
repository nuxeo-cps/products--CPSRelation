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
"""Test default node classes
"""

import unittest

import zope.component
import zope.interface

from Products.CPSRelation.interfaces import INode
from Products.CPSRelation.interfaces import IResource
from Products.CPSRelation.interfaces import IPrefixedResource
from Products.CPSRelation.interfaces import IBlank
from Products.CPSRelation.interfaces import ILiteral
from Products.CPSRelation.interfaces import IVersionResource
from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.interfaces import IRpathResource

from Products.CPSRelation.node import Resource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.node import Blank
from Products.CPSRelation.node import Literal
from Products.CPSRelation.node import VersionResource
from Products.CPSRelation.node import VersionHistoryResource
from Products.CPSRelation.node import RpathResource

from Products.CPSRelation.tests.CPSRelationTestCase import CPSRelationTestCase


class TestNodeBasic(unittest.TestCase):

    def test_Resource(self):
        zope.interface.verify.verifyClass(INode, Resource)
        zope.interface.verify.verifyClass(IResource, Resource)
        resource = Resource("http://example.org")
        self.assertEqual(resource.uri, "http://example.org")
        same_resource = Resource("http://example.org")
        other_resource = Resource("http://example2.org")
        self.assertEqual(resource, same_resource)
        self.assertEqual(hash(resource), hash(same_resource))
        self.assertNotEqual(resource, other_resource)
        self.assertNotEqual(hash(resource), hash(other_resource))

    def test_PrefixedResource(self):
        zope.interface.verify.verifyClass(INode, PrefixedResource)
        zope.interface.verify.verifyClass(IResource, PrefixedResource)
        zope.interface.verify.verifyClass(IPrefixedResource,
                                          PrefixedResource)
        resource = PrefixedResource("exp", "omar")
        self.assertEqual(resource.uri, "exp:omar")
        same_resource = PrefixedResource("exp", "omar")
        other_resource = PrefixedResource("exp", "bee")
        self.assertEqual(resource, same_resource)
        self.assertEqual(hash(resource), hash(same_resource))
        self.assertNotEqual(resource, other_resource)
        self.assertNotEqual(hash(resource), hash(other_resource))

    def test_Blank(self):
        zope.interface.verify.verifyClass(INode, Blank)
        zope.interface.verify.verifyClass(IBlank, Blank)
        blank = Blank("http://example.org")
        self.assertEqual(blank.id, "http://example.org")
        same_blank = Blank("http://example.org")
        other_blank = Blank("http://example2.org")
        self.assertEqual(blank, same_blank)
        self.assertEqual(hash(blank), hash(same_blank))
        self.assertNotEqual(blank, other_blank)
        self.assertNotEqual(hash(blank), hash(other_blank))

    def test_Literal(self):
        zope.interface.verify.verifyClass(INode, Literal)
        zope.interface.verify.verifyClass(ILiteral, Literal)
        lit = Literal("Héhé")
        self.assertEqual(lit.value, "Héhé")
        self.assertEqual(lit.language, None)
        self.assertEqual(lit.type, None)
        # test with unicode value
        same_lit = Literal(u'H\xe9h\xe9')
        other_lit = Literal("Héhéhé")
        self.assertEqual(lit, same_lit)
        self.assertEqual(hash(lit), hash(same_lit))
        self.assertNotEqual(lit, other_lit)
        self.assertNotEqual(hash(lit), hash(other_lit))

    def test_Literal_language(self):
        lit = Literal("Hoho", language="fr")
        self.assertEqual(lit.value, "Hoho")
        self.assertEqual(lit.language, 'fr')
        self.assertEqual(lit.type, None)
        # test with unicode value
        same_lit = Literal("Hoho", language="fr")
        other_lit = Literal("Hoho", language="be")
        self.assertEqual(lit, same_lit)
        self.assertEqual(hash(lit), hash(same_lit))
        self.assertNotEqual(lit, other_lit)
        self.assertNotEqual(hash(lit), hash(other_lit))

    def test_Literal_datatype(self):
        lit = Literal("Haha", type="str")
        self.assertEqual(lit.value, "Haha")
        self.assertEqual(lit.language, None)
        self.assertEqual(lit.type, 'str')
        # test with unicode value
        same_lit = Literal("Haha", type="str")
        other_lit = Literal("Haha", type="text")
        self.assertEqual(lit, same_lit)
        self.assertEqual(hash(lit), hash(same_lit))
        self.assertNotEqual(lit, other_lit)
        self.assertNotEqual(hash(lit), hash(other_lit))


class TestNodeExtended(unittest.TestCase):

    def test_VersionResource(self):
        zope.interface.verify.verifyClass(INode, VersionResource)
        zope.interface.verify.verifyClass(IResource, VersionResource)
        zope.interface.verify.verifyClass(IPrefixedResource,
                                          VersionResource)
        zope.interface.verify.verifyClass(IVersionResource,
                                          VersionResource)
        resource = VersionResource(docid="12345", revision=1)
        self.assertEqual(resource.uri, "uuid:12345__0001")
        self.assertEqual(resource.prefix, "uuid")
        self.assertEqual(resource.localname, "12345__0001")
        self.assertEqual(resource.docid, "12345")
        self.assertEqual(resource.revision, 1)
        same_resource = VersionResource(localname="12345__0001")
        self.assertEqual(same_resource.uri, "uuid:12345__0001")
        self.assertEqual(same_resource.prefix, "uuid")
        self.assertEqual(same_resource.localname, "12345__0001")
        self.assertEqual(same_resource.docid, "12345")
        self.assertEqual(same_resource.revision, 1)
        other_resource = VersionResource(localname="12345__0002")
        self.assertEqual(resource, same_resource)
        self.assertEqual(hash(resource), hash(same_resource))
        self.assertNotEqual(resource, other_resource)
        self.assertNotEqual(hash(resource), hash(other_resource))


    def test_VersionHistoryResource(self):
        zope.interface.verify.verifyClass(INode, VersionHistoryResource)
        zope.interface.verify.verifyClass(IResource, VersionHistoryResource)
        zope.interface.verify.verifyClass(IPrefixedResource,
                                          VersionHistoryResource)
        zope.interface.verify.verifyClass(IVersionHistoryResource,
                                          VersionHistoryResource)
        resource = VersionHistoryResource("12345")
        self.assertEqual(resource.uri, "docid:12345")
        self.assertEqual(resource.prefix, "docid")
        self.assertEqual(resource.localname, "12345")
        self.assertEqual(resource.docid, "12345")
        same_resource = VersionHistoryResource("12345")
        other_resource = VersionHistoryResource("666")
        self.assertEqual(resource, same_resource)
        self.assertEqual(hash(resource), hash(same_resource))
        self.assertNotEqual(resource, other_resource)
        self.assertNotEqual(hash(resource), hash(other_resource))


    def test_RpathResource(self):
        zope.interface.verify.verifyClass(INode, RpathResource)
        zope.interface.verify.verifyClass(IResource, RpathResource)
        zope.interface.verify.verifyClass(IPrefixedResource,
                                          RpathResource)
        zope.interface.verify.verifyClass(IRpathResource,
                                          RpathResource)
        resource = RpathResource("workspaces/toto")
        self.assertEqual(resource.uri, "rpath:workspaces/toto")
        self.assertEqual(resource.prefix, "rpath")
        self.assertEqual(resource.localname, "workspaces/toto")
        self.assertEqual(resource.rpath, "workspaces/toto")
        same_resource = RpathResource("workspaces/toto")
        other_resource = RpathResource("workspaces/tata")
        self.assertEqual(resource, same_resource)
        self.assertEqual(hash(resource), hash(same_resource))
        self.assertNotEqual(resource, other_resource)
        self.assertNotEqual(hash(resource), hash(other_resource))


class TestNodeAdapters(CPSRelationTestCase):

    def test_VersionResource(self):
        resource = IVersionResource(self.proxy1)
        self.assertEqual(resource.uri, "uuid:12345__0001")
        self.assertEqual(resource.prefix, "uuid")
        self.assertEqual(resource.localname, "12345__0001")
        self.assertEqual(resource.docid, "12345")
        self.assertEqual(resource.revision, 1)

    def test_VersionHistoryResource(self):
        resource = IVersionHistoryResource(self.proxy1)
        self.assertEqual(resource.uri, "docid:12345")
        self.assertEqual(resource.prefix, "docid")
        self.assertEqual(resource.localname, "12345")
        self.assertEqual(resource.docid, "12345")

    def test_RpathResource(self):
        resource = IRpathResource(self.proxy1)
        self.assertEqual(resource.uri, "rpath:workspaces/proxy1")
        self.assertEqual(resource.prefix, "rpath")
        self.assertEqual(resource.localname, "workspaces/proxy1")
        self.assertEqual(resource.rpath, "workspaces/proxy1")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNodeBasic))
    suite.addTest(unittest.makeSuite(TestNodeExtended))
    suite.addTest(unittest.makeSuite(TestNodeAdapters))
    return suite

