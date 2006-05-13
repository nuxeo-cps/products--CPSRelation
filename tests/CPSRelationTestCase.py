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
"""CPSRelation test case
"""

import os
import unittest

import zope.interface

from OFS.Folder import Folder

from Products.Five import zcml
from Products.CPSCore.interfaces import ICPSProxy
from Products.CPSCore.URLTool import URLTool

from Products.CPSRelation.interfaces import IVersionResource
from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.interfaces import IRpathResource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.node import Blank
from Products.CPSRelation.node import Literal
from Products.CPSRelation.statement import Statement

from Products.CPSRelation.tests import data as test_data

CPS_NAMESPACE_URI = "http://cps-project.org/2005/data/"


class FakeProxy(Folder):

    zope.interface.implements(ICPSProxy)

    def __init__(self, id, docid, revision):
        self.id = id
        self.docid = docid
        self.revision = revision

    def getDocId(self):
        return self.docid

    def getRevision(self):
        return self.revision


class CPSRelationTestCase(unittest.TestCase):

    def setUp(self):
        # load zcml configuration
        zcml.load_site()
        self.folder = Folder()
        # needed for rpath resources
        self.folder._setObject("portal_url", URLTool())
        # set a workspace
        self.folder._setObject('workspaces', Folder('workspaces'))
        workspaces = self.folder.workspaces
        workspaces._setObject("proxy1", FakeProxy("proxy1", "12345", 1))
        self.proxy1 = workspaces.proxy1
        workspaces._setObject("proxy2", FakeProxy("proxy2", "666", 2))
        self.proxy2 = workspaces.proxy2

    def tearDown(self):
        del self.folder
        del self.proxy1
        del self.proxy2


    # XXX: provide possibility to ignore order when comparing lists/tuples
    def assertEqual(self, first, second, msg=None, keep_order=True):
        if not keep_order:
            if isinstance(first, (list, tuple)):
                first_list = list(first)
                first_list.sort()
                first = tuple(first_list)
            if isinstance(second, (list, tuple)):
                second_list = list(second)
                second_list.sort()
                second = tuple(second_list)
        return unittest.TestCase.assertEqual(self, first, second, msg)

    assertEquals = assertEqual

    # helper methods

    def addBaseRelations(self, graph):
        # relations with resources, blank nodes and literals
        statements = [
            Statement(PrefixedResource('cps', 'cps'),
                      PrefixedResource('cps', 'title'),
                      Literal('CPS Project')),
            Statement(PrefixedResource('cps', 'cps'),
                      PrefixedResource('cps', 'techno'),
                      Blank('techno')),
            Statement(Blank('techno'),
                      PrefixedResource('cps', 'title'),
                      Literal('Zope/CPS')),
            ]
        graph.add(statements)
        self.base_relations = statements


    def addVersionRelations(self, graph):
        statements = [
            Statement(IVersionResource(self.proxy1),
                      PrefixedResource('cps', 'title'),
                      Literal("First proxy")),
            Statement(IVersionResource(self.proxy2),
                      PrefixedResource('cps', 'title'),
                      Literal("Second proxy")),
            ]
        graph.add(statements)
        self.version_relations = statements


    def addVersionHistoryRelations(self, graph):
        statements = [
            Statement(IVersionHistoryResource(self.proxy1),
                      PrefixedResource('cps', 'title'),
                      Literal("First proxy")),
            Statement(IVersionHistoryResource(self.proxy2),
                      PrefixedResource('cps', 'title'),
                      Literal("Second proxy")),
            ]
        graph.add(statements)
        self.versionhistory_relations = statements


    def addRpathRelations(self):
        statements = [
            Statement(IRpathResource(self.proxy1),
                      PrefixedResource('cps', 'title'),
                      Literal("First proxy")),
            Statement(IRpathResource(self.proxy2),
                      PrefixedResource('cps', 'title'),
                      Literal("Second proxy")),
            ]
        graph.add(statements)
        self.rpath_relations = statements


    def getTestData(self, file_rpath):
        file_path = os.path.join(test_data.__path__[0], file_rpath)
        try:
            f = open(file_path, 'r')
        except IOError:
            raise ValueError("file %s not found" % file_path)
        else:
            data = f.read()
            f.close()
        return data
